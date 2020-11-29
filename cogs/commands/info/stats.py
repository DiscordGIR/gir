import discord
from discord.ext import commands
import os
import psutil
from math import floor
import datetime
import humanize

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.datetime.now()

    @commands.guild_only()
    @commands.command(name="stats")
    async def stats(self, ctx):
        process = psutil.Process(os.getpid())
        diff = datetime.datetime.now() - self.start_time
        diff = humanize.naturaldelta(diff)

        embed = discord.Embed(title=f"{self.bot.user.name} Statistics", color=discord.Color.blurple())
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.add_field(name="Bot Version", value=discord.__version__)
        embed.add_field(name="Uptime", value=diff)
        embed.add_field(name="Memory Usage", value=f"{floor(process.memory_info().rss/1000/1000)} MB")
        
        await ctx.message.reply(embed=embed)

def setup(bot):
    bot.add_cog(Stats(bot))
