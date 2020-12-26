import discord
import asyncio
import datetime
import pytimeparse
import random
from discord.ext import commands

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="giveaway")
    @commands.guild_only()
    @commands.max_concurrency(1, per=commands.BucketType.member, wait=False)

    #TODO: Add channel specification
    #TODO: Possibly allow specifying giveaway parameters via arguments without prompts?

    async def giveaway(self, ctx, *, action: str):
        """
        Start or manage giveaways (Admin only)

        Example Use:
        ------------
        !giveaway start (You will be prompted for a name, sponsor, and the time until end)
        !giveaway end (You will be prompted for the message ID of the giveaway)
        !giveaway reroll (You will be prompted for the message ID of the giveaway)

        Parameters:
        -----------
        action: str
            Action to perform (currently start, end, reroll)
        """

        def wait_check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        if not ctx.guild.id == self.bot.settings.guild_id:
            return
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 6):
            raise commands.BadArgument(
                "You do not have permission to use this command.")

        if action == "start":

            # TODO: Make this less repetitive

            name = None

            prompt = await ctx.message.reply("Enter a name for the giveaway (or type cancel to cancel)")
            try:
                m_name = await self.bot.wait_for('message', check=wait_check, timeout=120)
            except asyncio.TimeoutError:
                return
            else:
                await m_name.delete()
                await prompt.delete()
                if m_name.content.lower() == "cancel":
                    return
                elif m_name.content is not None and m_name.content != "":
                    name = m_name.content

            sponsor = None
            prompt = await ctx.message.reply("Enter the sponsor's user ID (or type cancel to cancel)")
            try:
                m_sponsor = await self.bot.wait_for('message', check=wait_check, timeout=120)
            except asyncio.TimeoutError:
                return
            else:
                await m_sponsor.delete()
                await prompt.delete()
                if m_sponsor.content.lower() == "cancel":
                    return
                elif m_sponsor.content is not None and m_sponsor.content != "":
                    sponsor = m_sponsor.content
            
            end_time = None
            prompt = await ctx.message.reply("Enter the time until the giveaway ends (or type cancel to cancel)")
            try:
                m_time = await self.bot.wait_for('message', check=wait_check, timeout=120)
            except asyncio.TimeoutError:
                return
            else:
                await m_time.delete()
                await prompt.delete()
                if m_time.content.lower() == "cancel":
                    return
                elif m_time.content is not None and m_time.content != "":
                    now = datetime.datetime.now()
                    delta = pytimeparse.parse(m_time.content)
                    end_time = now + datetime.timedelta(seconds=delta)
            
            embed = discord.Embed(title=name)
            embed.description = f"Hosted by <@{sponsor}>"
            embed.timestamp = end_time
            embed.set_footer(text="Ends")

            message = await ctx.send(embed=embed)
            await message.add_reaction("✅")

            await ctx.message.delete()

            self.bot.settings.tasks.schedule_end_giveaway(channel_id=message.channel.id, message_id=message.id, date=end_time)

        elif action == "reroll":
            g_id = None

            prompt = await ctx.message.reply("Enter the ID to reroll for (or type cancel to cancel)")
            try:
                m_id = await self.bot.wait_for('message', check=wait_check, timeout=120)
            except asyncio.TimeoutError:
                return
            else:
                await m_id.delete()
                await prompt.delete()
                if m_id.content.lower() == "cancel":
                    return
                elif m_id.content is not None and m_id.content != "":
                    g_id = int(m_id.content)
            
            giveaway = await self.bot.settings.get_giveaway(id=g_id)
            new_rand_id = random.choice(giveaway.entries)
            
            await ctx.message.delete()
            await ctx.send(f"**Reroll**\nThe new winner of the giveaway of **{giveaway.name}** is <@{new_rand_id}>! Congratulations!")
            
def setup(bot):
    bot.add_cog(Giveaway(bot))