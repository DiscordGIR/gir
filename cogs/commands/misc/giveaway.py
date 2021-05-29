import asyncio
import datetime
import random
import traceback

import cogs.utils.permission_checks as permissions
import discord
import humanize
import pytimeparse
from cogs.utils.tasks import end_giveaway
from data.giveaway import Giveaway as GiveawayDB
from discord.ext import commands, tasks


class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.giveaway_messages = {}
        self.time_updater_loop.start()

    def cog_unload(self):
        self.time_updater_loop.cancel()

    async def prompt(self, ctx, data, _type):
        question = data['prompt']
        convertor = data['convertor']

        def wait_check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        ret = None
        prompt = await ctx.send(embed=discord.Embed(description=question, color=discord.Color.blurple()))
        try:
            response = await self.bot.wait_for('message', check=wait_check, timeout=120)
        except asyncio.TimeoutError:
            await prompt.delete()
            return
        else:
            await response.delete()
            await prompt.delete()
            if response.content.lower() == "cancel":
                return
            elif response.content is not None and response.content != "":
                if _type in ['name', 'winners', 'time']:
                    ret = convertor(response.content)
                    if _type == 'winners' and ret < 1:
                        raise commands.BadArgument("Can't have less than 1 winner")
                    if ret is None:
                        raise commands.BadArgument(f"Improper value given for {_type}")
                else:
                    ret = await convertor(ctx, response.content)
        return ret

    @commands.guild_only()
    @permissions.admin_and_up()
    @commands.max_concurrency(1, per=commands.BucketType.member, wait=False)
    @commands.group()
    async def giveaway(self, ctx):
        """
        Manage giveaways using !giveaway <action>, choosing from below...
        """

        if ctx.invoked_subcommand is None:
            raise commands.BadArgument("Invalid giveaway subcommand passed. Options: `start`, `reroll`, `end`")

    @giveaway.command()
    async def start(self, ctx, sponsor: discord.Member = None, time: str = None, winners: int = -1, channel: discord.TextChannel = None):
        """Start a giveaway. Use `!giveaway start` and follow the prompts, or see the example.

        Example Use:
        ------------
        !giveaway start (You will be prompted for all info)
        !giveaway start @habibi test#1531 30s 1 #bot-commands

        Parameters
        ----------
        sponsor : discord.Member
            Who sponsored the giveaway
        time : str, optional
            When to end, by default None
        winners : int
            How many winners
        channel : discord.TextChannel, optional
            Channel to post giveway in
        """

        prompts = {
            'name': {
                'convertor': str,
                'prompt': "Enter a name for the giveaway (or type cancel to cancel)"
                },
            'sponsor': {
                'convertor': commands.MemberConverter().convert,
                'prompt': "Tag or give the ID of the sponsor of this giveaway (or type cancel to cancel)"
                },
            'time': {
                'convertor': pytimeparse.parse,
                'prompt': "How long should this giveaway last? (e.g 10m) (or type cancel to cancel)"
                },
            'winners': {
                'convertor': int,
                'prompt': "How many winners should this giveaway have? (or type cancel to cancel)"
                },
            'channel': {
                'convertor': commands.TextChannelConverter().convert,
                'prompt': "Mention the channel to post the giveaway in (or type cancel to cancel)"
                }
        }

        responses = {
            'name': None,
            'sponsor': sponsor,
            'time': pytimeparse.parse(time) if time is not None else None,
            'winners': None if winners < 1 else winners,
            'channel': channel
        }

        for response in responses:
            if responses[response] is None:
                res = await self.prompt(ctx=ctx, data=prompts[response], _type=response)
                if res is None:
                    raise commands.BadArgument("Command cancelled.")
                responses[response] = res

        now = datetime.datetime.now()
        delta = responses['time']
        end_time = now + datetime.timedelta(seconds=delta)

        embed = discord.Embed(title="New giveaway!")
        embed.description = f"**{responses['name']}** is being given away by {responses['sponsor'].mention} to **{responses['winners']}** lucky {'winner' if responses['winners'] == 1 else 'winners'}!"
        embed.add_field(name="Time remaining", value=f"Less than {humanize.naturaldelta(end_time - now)}")
        embed.timestamp = end_time
        embed.color = discord.Color.random()
        embed.set_footer(text="Ends")

        message = await responses['channel'].send(embed=embed)
        await message.add_reaction("🎉")

        await ctx.message.delete()

        giveaway = GiveawayDB(_id=message.id, channel=responses['channel'].id, name=responses['name'], winners=responses['winners'], end_time=end_time, sponsor=responses['sponsor'].id)
        giveaway.save()

        if ctx.channel.id != responses['channel'].id:
            await ctx.send(f"Giveaway started!", embed=embed, delete_after=10)

        self.bot.settings.tasks.schedule_end_giveaway(channel_id=responses['channel'].id, message_id=message.id, date=end_time, winners=responses['winners'])

    @tasks.loop(seconds=360)
    async def time_updater_loop(self):
        guild = self.bot.get_guild(self.bot.settings.guild_id)
        if guild is None:
            return

        giveaways = GiveawayDB.objects(is_ended=False)
        for giveaway in giveaways:
            await self.do_giveaway_update(giveaway, guild)

    # @commands.Cog.listener()
    # async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
    #     if payload.member.bot:
    #         return
    #     if not payload.guild_id:
    #         return
    #     if not payload.guild_id == self.bot.settings.guild_id:
    #         return

    #     g = await self.bot.settings.get_giveaway(id=payload.message_id)
    #     await self.do_giveaway_update(g, payload.member.guild)

    async def do_giveaway_update(self, giveaway: GiveawayDB, guild: discord.Guild):
        if giveaway is None:
            return
        if giveaway.is_ended:
            return

        now = datetime.datetime.now()
        end_time = giveaway.end_time
        if end_time is None or end_time < now:
            return

        channel = guild.get_channel(giveaway.channel)

        if giveaway._id in self.giveaway_messages:
            message = self.giveaway_messages[giveaway._id]
        else:
            try:
                message = await channel.fetch_message(giveaway._id)
                self.giveaway_messages[giveaway._id] = message
            except Exception:
                return

        if len(message.embeds) == 0:
            return

        embed = message.embeds[0]
        embed.set_field_at(0, name="Time remaining", value=f"Less than {humanize.naturaldelta(end_time - now)}")
        await message.edit(embed=embed)

    @giveaway.command()
    async def reroll(self, ctx, message_id: int):
        """Pick a new winner of an already ended giveaway.

        Example usage
        -------------
        !giveaway reroll 795120157679812670

        Parameters
        ----------
        message : int
            ID of the giveaway message
        """

        g = await self.bot.settings.get_giveaway(_id=message_id)

        if g is None:
            raise commands.BadArgument("Couldn't find an ended giveaway by the provided ID.")
        elif not g.is_ended:
            raise commands.BadArgument("That giveaway hasn't ended yet!")
        elif len(g.entries) == 0:
            raise commands.BadArgument(f"There are no entries for the giveaway of **{g.name}**.")
        elif len(g.entries) <= len(g.previous_winners):
            raise commands.BadArgument("No more winners are possible!")

        the_winner = None
        while the_winner is None:
            random_id = random.choice(g.entries)
            the_winner = ctx.guild.get_member(random_id)
            if the_winner is not None and the_winner.id not in g.previous_winners:
                break
            the_winner = None

        g.previous_winners.append(the_winner.id)
        g.save()

        await ctx.message.delete()
        channel = ctx.guild.get_channel(g.channel)

        await channel.send(f"**Reroll**\nThe new winner of the giveaway of **{g.name}** is {the_winner.mention}! Congratulations!")
        await ctx.send(embed=discord.Embed(description="Rerolled!", color=discord.Color.blurple()), delete_after=5)

    @giveaway.command()
    async def end(self, ctx, message_id: int):
        """End a giveaway early

        Example usage
        -------------
        !giveaway end 795120157679812670

        Parameters
        ----------
        message : int
            ID of the giveaway message
        """

        giveaway = await self.bot.settings.get_giveaway(_id=message_id)
        if giveaway is None:
            raise commands.BadArgument("A giveaway with that ID was not found.")
        elif giveaway.is_ended:
            raise commands.BadArgument("That giveaway has already ended.")

        await ctx.message.delete()
        self.bot.settings.tasks.tasks.remove_job(str(message_id + 2), 'default')
        await end_giveaway(giveaway.channel, message_id, giveaway.winners)

        await ctx.send(embed=discord.Embed(description="Giveaway ended!", color=discord.Color.blurple()), delete_after=5)

    @time_updater_loop.error
    @giveaway.error
    @start.error
    @end.error
    @reroll.error
    async def info_error(self, ctx, error):
        await ctx.message.delete(delay=5)
        if (isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, Permissions.PermissionsFailure)
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.MissingPermissions)
            or isinstance(error, commands.CommandInvokeError)
            or isinstance(error, commands.CommandOnCooldown)
            or isinstance(error, commands.BotMissingPermissions)
            or isinstance(error, commands.MaxConcurrencyReached)
                or isinstance(error, commands.NoPrivateMessage)):
            await self.bot.send_error(ctx, error)
        else:
            await self.bot.send_error(ctx, "A fatal error occured. Tell <@109705860275539968> about this.")
            traceback.print_exc()


def setup(bot):
    bot.add_cog(Giveaway(bot))
