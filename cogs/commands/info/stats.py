import datetime
import os
import platform
import traceback
from math import floor

import discord
import humanize
import psutil
from asyncio import sleep
from discord.ext import commands


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.datetime.now()

    @commands.guild_only()
    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context) -> None:
        """Pong

        Example usage:
        `!ping`

        """
        bot_chan = self.bot.settings.guild().channel_botspam
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 5) and ctx.channel.id != bot_chan:
            raise commands.BadArgument(
                f"Command only allowed in <#{bot_chan}>")

        b = datetime.datetime.utcnow()
        embed = discord.Embed(
            title=f"Pong!", color=discord.Color.blurple())
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.description = "Latency: testing..."

        m = await ctx.message.reply(embed=embed)
        ping = floor((datetime.datetime.utcnow() - b).total_seconds() * 1000)
        await sleep(1)
        embed.description = f"Latency: {ping} ms"
        await m.edit(embed=embed)

    @commands.guild_only()
    @commands.command(name="stats")
    async def stats(self, ctx: commands.Context) -> None:
        """Statistics about the bot

        Example usage:
        `!stats`

        """

        bot_chan = self.bot.settings.guild().channel_botspam
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 5) and ctx.channel.id != bot_chan:
            raise commands.BadArgument(
                f"Command only allowed in <#{bot_chan}>")

        process = psutil.Process(os.getpid())
        diff = datetime.datetime.now() - self.start_time
        diff = humanize.naturaldelta(diff)

        embed = discord.Embed(
            title=f"{self.bot.user.name} Statistics", color=discord.Color.blurple())
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.add_field(name="Uptime", value=diff)
        embed.add_field(name="CPU Usage", value=f"{psutil.cpu_percent()}%")
        embed.add_field(name="Memory Usage",
                        value=f"{floor(process.memory_info().rss/1000/1000)} MB")
        embed.add_field(name="Python Version", value=platform.python_version())

        await ctx.message.reply(embed=embed)

    @commands.guild_only()
    @commands.command(name="serverinfo")
    async def serverinfo(self, ctx: commands.Context) -> None:
        """Displays info about the server

        Example usage:
        `!serverinfo`

        """
        bot_chan = self.bot.settings.guild().channel_botspam
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 5) and ctx.channel.id != bot_chan:
            raise commands.BadArgument(
                f"Command only allowed in <#{bot_chan}>")

        guild = ctx.guild

        embed = discord.Embed(title="Server Information")
        embed.color = discord.Color.blurple()
        embed.set_thumbnail(url=guild.icon_url)
        embed.add_field(name="Region", value=guild.region, inline=True)
        embed.add_field(name="Boost Tier",
                        value=guild.premium_tier, inline=True)
        embed.add_field(name="Users", value=guild.member_count, inline=True)
        embed.add_field(name="Channels", value=len(
            guild.channels) + len(guild.voice_channels), inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
        embed.add_field(name="Created", value=guild.created_at.strftime(
            "%B %d, %Y, %I:%M %p"), inline=True)

        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.message.reply(embed=embed)

    @serverinfo.error
    @stats.error
    @ping.error
    async def info_error(self, ctx, error):
        await ctx.message.delete(delay=5)
        if (isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.MissingPermissions)
                or isinstance(error, commands.NoPrivateMessage)):
            await self.bot.send_error(ctx, error)
        else:
            await self.bot.send_error(ctx, "A fatal error occured. Tell <@109705860275539968> about this.")
            traceback.print_exc()


def setup(bot):
    bot.add_cog(Stats(bot))
