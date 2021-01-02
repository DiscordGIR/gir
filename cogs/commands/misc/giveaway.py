import discord
import asyncio
import datetime
import pytimeparse
import random
from cogs.utils.tasks import end_giveaway
from discord.ext import commands

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def prompt(self, ctx, question: str):
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
                ret = response
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

        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid giveaway subcommand passed. Options: `start`, `reroll`, `end`")
    
    @giveaway.command()
    async def start(self, ctx, *args):
        name = None
        sponsor = None
        time = None
        winners = None
        channel = None
        if len(args) <= 0: # we have to prompt for everything

            name = await self.prompt(ctx=ctx, question="Enter a name for the giveaway (or type cancel to cancel)")
            if name is None:
                await ctx.message.delete()
                await ctx.send("Command cancelled.", delete_after=5)
                return
            name = name.content

            sponsor = await self.prompt(ctx, "Enter the sponsor's user ID (or type cancel to cancel)")
            if sponsor is None:
                await ctx.message.delete()
                await ctx.send("Command cancelled.", delete_after=5)
                return
            sponsor = int(sponsor.content)

            time = await self.prompt(ctx, "Enter the time until the giveaway ends (or type cancel to cancel)")
            if time is None:
                await ctx.message.delete()
                await ctx.send("Command cancelled.", delete_after=5)
                return
            time = time.content

            winners = await self.prompt(ctx, "Enter the amount of winners for the giveaway (or type cancel to cancel)")
            if winners is None:
                await ctx.message.delete()
                await ctx.send("Command cancelled.", delete_after=5)
                return
            winners = int(winners.content)

            channel = await self.prompt(ctx, "Mention the channel to post the giveaway in (or type cancel to cancel)")
            if channel is None:
                await ctx.message.delete()
                await ctx.send("Command cancelled.", delete_after=5)
                return
            channel = channel.channel_mentions[0]
            if channel is None:
                await ctx.message.delete()
                await ctx.send("Could not find a channel with the mention you provided.")
                return

        elif len(args) == 1:

            name = args[0]

            sponsor = await self.prompt(ctx, "Enter the sponsor's user ID (or type cancel to cancel)")
            if sponsor is None:
                await ctx.message.delete()
                await ctx.send("Command cancelled.", delete_after=5)
                return
            sponsor = int(sponsor.content)

            time = await self.prompt(ctx, "Enter the time until the giveaway ends (or type cancel to cancel)")
            if time is None:
                await ctx.message.delete()
                await ctx.send("Command cancelled.", delete_after=5)
                return
            time = time.content

            winners = await self.prompt(ctx, "Enter the amount of winners for the giveaway (or type cancel to cancel)")
            if winners is None:
                await ctx.message.delete()
                await ctx.send("Command cancelled.", delete_after=5)
                return
            winners = int(winners.content)

            channel = await self.prompt(ctx, "Mention the channel to post the giveaway in (or type cancel to cancel)")
            if channel is None:
                await ctx.message.delete()
                await ctx.send("Command cancelled.", delete_after=5)
                return
            channel = channel.channel_mentions[0]
            if channel is None:
                await ctx.message.delete()
                await ctx.send("Could not find a channel with the mention you provided.")
                return
                
        elif len(args) == 2:
            name = args[0]
            sponsor = args[1]

            time = await self.prompt(ctx, "Enter the time until the giveaway ends (or type cancel to cancel)")
            if time is None:
                await ctx.message.delete()
                await ctx.send("Command cancelled.", delete_after=5)
                return
            time = time.content

            winners = await self.prompt(ctx, "Enter the amount of winners for the giveaway (or type cancel to cancel)")
            if winners is None:
                await ctx.message.delete()
                await ctx.send("Command cancelled.", delete_after=5)
                return
            winners = int(winners.content)

            channel = await self.prompt(ctx, "Mention the channel to post the giveaway in (or type cancel to cancel)")
            if channel is None:
                await ctx.message.delete()
                await ctx.send("Command cancelled.", delete_after=5)
                return
            channel = channel.channel_mentions[0]
            if channel is None:
                await ctx.message.delete()
                await ctx.send("Could not find a channel with the mention you provided.")
                return

        elif len(args) == 3:
            name = args[0]
            sponsor = args[1]
            time = args[2]

            winners = await self.prompt(ctx, "Enter the amount of winners for the giveaway (or type cancel to cancel)")
            if winners is None:
                await ctx.message.delete()
                await ctx.send("Command cancelled.", delete_after=5)
                return
            winners = int(winners.content)

            channel = await self.prompt(ctx, "Mention the channel to post the giveaway in (or type cancel to cancel)")
            if channel is None:
                await ctx.message.delete()
                await ctx.send("Command cancelled.", delete_after=5)
                return
            channel = channel.channel_mentions[0]
            if channel is None:
                await ctx.message.delete()
                await ctx.send("Could not find a channel with the mention you provided.")
                return
        
        elif len(args) == 4:
            name = args[0]
            sponsor = args[1]
            time = args[2]
            winners = int(args[3])

            channel = await self.prompt(ctx, "Mention the channel to post the giveaway in (or type cancel to cancel)")
            if channel is None:
                await ctx.message.delete()
                await ctx.send("Command cancelled.", delete_after=5)
                return
            channel = channel.channel_mentions[0]
            if channel is None:
                await ctx.message.delete()
                await ctx.send("Could not find a channel with the mention you provided.")
                return
        
        elif len(args) >= 5:
            name = args[0]
            sponsor = args[1]
            time = args[2]
            winners = int(args[3])
            channel = ctx.message.channel_mentions[0]
            if channel is None:
                await ctx.message.delete()
                await ctx.send("Could not find a channel with the mention you provided.")
                return
        
        if name is not None and sponsor is not None and time is not None and winners is not None and channel is not None:
            now = datetime.datetime.now()
            delta = pytimeparse.parse(time)
            end_time = now + datetime.timedelta(seconds=delta)

            embed = discord.Embed(title=name)
            embed.description = f"Hosted by <@{sponsor}>\n{winners} {'winner' if winners == 1 else 'winners'}"
            embed.timestamp = end_time
            embed.set_footer(text="Ends")

            message = await channel.send(embed=embed)
            await message.add_reaction("✅")

            await ctx.message.delete()

            self.bot.settings.tasks.schedule_end_giveaway(channel_id=channel.id, message_id=message.id, date=end_time, winners=winners)
        else:
            await ctx.message.delete()
            await ctx.send("Command cancelled.")
    
    @giveaway.command()
    async def reroll(self, ctx, *args):
        message_id = None
        if len(args) <= 0:
            message_id = await self.prompt(ctx, "Enter the message ID of the giveaway to reroll (or type cancel to cancel)")
            if message_id is None:
                await ctx.message.delete()
                await ctx.send("Command cancelled.")
                return
            message_id = int(message_id.content)
        else:
            message_id = int(args[0])
        
        g = await self.bot.settings.get_giveaway(id=message_id)

        if g is None:
            await ctx.message.delete()
            await ctx.send("Couldn't find an ended giveaway by the provided ID.")
            return

        new_rand_ids = random.sample(g.entries, g.winners)
        mentions = []
        for user_id in new_rand_ids:
            member = ctx.guild.get_member(user_id)
            while member is None or member.mention in mentions: # ensure that member hasn't left the server while simultaneously ensuring that we don't add duplicate members if we select a new random one
                member = ctx.guild.get_member(random.choice(g.entries))
            mentions.append(member.mention)

        await ctx.message.delete()

        if not mentions:
            await ctx.send(f"There are no entries for the giveaway of **{embed.title}**.")
            return
        
        channel = ctx.guild.get_channel(g.channel)

        if g.winners == 1:
            await channel.send(f"**Reroll**\nThe new winner of the giveaway of **{g.name}** is {mentions[0]}! Congratulations!")
        else:
            await channel.send(f"**Reroll**\nThe new winners of the giveaway of **{g.name}** are {', '.join(mentions)}! Congratulations!")
    
    @giveaway.command()
    async def end(self, ctx, *args):
        channel = None
        message_id = None
        winners = None
        if len(args) <= 0:

            c_msg = await self.prompt(ctx, "Mention the channel that the giveaway is in (or type cancel to cancel)")
            if c_msg is None:
                await ctx.message.delete()
                await ctx.send("Command cancelled.")
                return
            channel = c_msg.channel_mentions[0]
            if channel is None:
                await ctx.message.delete()
                await ctx.send("Could not find a channel from what you provided.")
                return

            message_id = await self.prompt(ctx, "Enter the message ID of the giveaway to end early (or type cancel to cancel)")
            if message_id is None:
                await ctx.message.delete()
                await ctx.send("Command cancelled.")
                return
            message_id = int(message_id.content)

            winners = await self.prompt(ctx, "Enter amount of winners to select (or type cancel to cancel)")
            if winners is None:
                await ctx.message.delete()
                await ctx.send("Command cancelled", delete_after=5)
                return
            winners = int(winners.content)

        elif len(args) == 1:

            channel = ctx.message.channel_mentions[0]
            if channel is None:
                await ctx.message.delete()
                await ctx.send("Could not find a channel from what you provided.")
                return

            message_id = await self.prompt(ctx, "Enter the message ID of the giveaway to end early (or type cancel to cancel)")
            if message_id is None:
                await ctx.message.delete()
                await ctx.send("Command cancelled.")
                return
            message_id = int(message_id.content)

            winners = await self.prompt(ctx, "Enter amount of winners to select (or type cancel to cancel)")
            if winners is None:
                await ctx.message.delete()
                await ctx.send("Command cancelled", delete_after=5)
                return
            winners = int(winners.content)

        elif len(args) == 2:
            channel = ctx.message.channel_mentions[0]
            if channel is None:
                await ctx.message.delete()
                await ctx.send("Could not find a channel from what you provided.")
                return

            message_id = int(args[1])

            winners = await self.prompt(ctx, "Enter amount of winners to select (or type cancel to cancel)")
            if winners is None:
                await ctx.message.delete()
                await ctx.send("Command cancelled", delete_after=5)
                return
            winners = int(winners.content)

        else:

            channel = ctx.message.channel_mentions[0]
            if channel is None:
                await ctx.message.delete()
                await ctx.send("Could not find a channel from what you provided.")
                return

            message_id = int(args[0])

            winners = int(args[0])
        
        await ctx.message.delete()
        self.bot.settings.tasks.tasks.remove_job(str(message_id + 1), 'default')
        await end_giveaway(channel.id, message_id, winners)
            
def setup(bot):
    bot.add_cog(Giveaway(bot))