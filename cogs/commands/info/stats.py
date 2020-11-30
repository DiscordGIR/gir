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
    async def stats(self, ctx: commands.Context) -> None:
        """!stats

        Statistics about the bot

        Parameters
        ----------
        None
        """
        process = psutil.Process(os.getpid())
        diff = datetime.datetime.now() - self.start_time
        diff = humanize.naturaldelta(diff)

        embed = discord.Embed(title=f"{self.bot.user.name} Statistics", color=discord.Color.blurple())
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.add_field(name="Bot Version", value=discord.__version__)
        embed.add_field(name="Uptime", value=diff)
        embed.add_field(name="Memory Usage", value=f"{floor(process.memory_info().rss/1000/1000)} MB")
        
        await ctx.message.reply(embed=embed)

    @commands.guild_only()
    @commands.command(name="serverinfo")
    async def serverinfo(self, ctx: discord.Client) -> None:
        """!serverinfo

        Displays info about the server

        Parameters
        ----------
        None
        """
        guild = ctx.guild

        embed=discord.Embed(title="Server Information")
        embed.color = discord.Color.blurple()
        embed.set_image(url=guild.icon_url)
        embed.add_field(name="Region", value=guild.region, inline=True)
        embed.add_field(name="Boost Tier", value=guild.premium_tier, inline=True)
        embed.add_field(name="Users", value=guild.member_count, inline=True)
        embed.add_field(name="Channels", value=len(guild.channels) + len(guild.voice_channels), inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
        embed.add_field(name="Created", value=guild.created_at.strftime("%B %d, %Y, %I:%M %p"), inline=True)
        
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.message.reply(embed=log)


    @serverinfo.error
    @stats.error
    async def info_error(self, ctx, error):
        if (isinstance(error, commands.MissingRequiredArgument) 
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.MissingPermissions)
            or isinstance(error, commands.NoPrivateMessage)):
                await self.bot.send_error(ctx, error)
        else:
            traceback.print_exc()
def setup(bot):
    bot.add_cog(Stats(bot))
