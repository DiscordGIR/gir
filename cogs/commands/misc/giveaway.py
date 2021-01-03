import discord
import asyncio
import datetime
import pytimeparse
import random
import traceback
from cogs.utils.tasks import end_giveaway
from data.giveaway import Giveaway as GiveawayDB
from discord.ext import commands


class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def prompt(self, ctx, data, _type):
        question = data['prompt']
        convertor = data['convertor']
        
        def wait_check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        ret = None
        prompt = await ctx.send(question)
        try:
            response = await self.bot.wait_for('message', check=wait_check, timeout=120)
        except asyncio.TimeoutError:
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

    #@commands.command(name="giveaway")
    @commands.guild_only()
    @commands.max_concurrency(1, per=commands.BucketType.member, wait=False)

    #TODO: Possibly make prompting/arg parsing code less repetitive

    @commands.group()
    async def giveaway(self, ctx):
        """
        Start or manage giveaways (Admin only)

        Example Use:
        ------------
        !giveaway start (You will be prompted for a name, sponsor, the time until end, the amount of winners, and the channel)
        !giveaway end (You will be prompted for the message ID of the giveaway)
        !giveaway reroll (You will be prompted for the message ID of the giveaway)
        """

        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 6):
            raise commands.BadArgument(
                "You need to be an administrator or higher to use that command.")

        if ctx.invoked_subcommand is None:
            raise commands.BadArgument("Invalid giveaway subcommand passed. Options: `start`, `reroll`, `end`")

    @giveaway.command()
    # async def start(self, ctx, *args):
    async def start(self, ctx, sponsor: discord.Member = None, time: str = None, winners: int = -1, channel: discord.TextChannel = None):
        prompts = {
            'name': {
                'convertor': str,
                'prompt': "Enter a name for the giveaway (or type cancel to cancel)"
                },
            'sponsor': {
                'convertor': commands.MemberConverter().convert,
                'prompt': "Enter the sponsor's user ID (or type cancel to cancel)"
                },
            'time': {
                'convertor': pytimeparse.parse,
                'prompt': "Enter the time until the giveaway ends (or type cancel to cancel)"
                },
            'winners': {
                'convertor': int,
                'prompt': "Enter the amount of winners for the giveaway (or type cancel to cancel)"
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

        embed = discord.Embed(title=responses['name'])
        embed.description = f"Hosted by {responses['sponsor'].mention}\n{responses['winners']} {'winner' if responses['winners'] == 1 else 'winners'}"
        embed.timestamp = end_time
        embed.set_footer(text="Ends")

        message = await channel.send(embed=embed)
        await message.add_reaction("✅")

        await ctx.message.delete()

        giveaway = GiveawayDB(_id=message.id, channel=responses['channel'].id, name=responses['name'], winners=responses['winners'])
        giveaway.save()

        await ctx.send(f"Giveaway started!", embed=embed, delete_after=10)
        
        self.bot.settings.tasks.schedule_end_giveaway(channel_id=channel.id, message_id=message.id, date=end_time, winners=responses['winners'])

    @giveaway.command()
    async def reroll(self, ctx, message: discord.Message):
        g = await self.bot.settings.get_giveaway(id=message.id)

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
            print(the_winner.id not in g.previous_winners)
            if the_winner is not None and the_winner.id not in g.previous_winners:
                break

        g.previous_winners.append(the_winner.id)
        g.save()
        
        await ctx.message.delete()
        channel = ctx.guild.get_channel(g.channel)

        # if g.winners == 1:
        await channel.send(f"**Reroll**\nThe new winner of the giveaway of **{g.name}** is {the_winner.mention}! Congratulations!")
        # else:
        #     await channel.send(f"**Reroll**\nThe new winners of the giveaway of **{g.name}** are {', '.join(mentions)}! Congratulations!")

    @giveaway.command()
    async def end(self, ctx, message: discord.Message):
        giveaway = self.bot.settings.get_giveaway(_id=message.id)
        if giveaway is None:
            raise commands.BadArgument("A giveaway with that ID was not found.")

        await ctx.message.delete()
        self.bot.settings.tasks.tasks.remove_job(str(message.id + 2), 'default')
        await end_giveaway(message.channel.id, message.id, giveaway.winners)

    @giveaway.error
    @start.error   
    @end.error   
    @reroll.error   
    async def info_error(self, ctx, error):
        await ctx.message.delete(delay=5)
        if (isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.MissingPermissions)
            or isinstance(error, commands.CommandInvokeError)
            or isinstance(error, commands.CommandOnCooldown)
            or isinstance(error, commands.BotMissingPermissions)
            or isinstance(error, commands.MaxConcurrencyReached)
                or isinstance(error, commands.NoPrivateMessage)):
            await self.bot.send_error(ctx, error)
            traceback.print_exc()
        else:
            await self.bot.send_error(ctx, "A fatal error occured. Tell <@109705860275539968> about this.")
            traceback.print_exc()


def setup(bot):
    bot.add_cog(Giveaway(bot))
