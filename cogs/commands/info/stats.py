import datetime
import os
import platform
import traceback
from asyncio import sleep
from math import floor

import cogs.utils.context as context
import cogs.utils.permission_checks as permissions
import discord
import humanize
import psutil
from discord.ext import commands


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.datetime.now()

    @commands.guild_only()
    @commands.command(name="roleinfo")
    @permissions.bot_channel_only_unless_mod()
    async def roleinfo(self, ctx: context.Context, role: discord.Role) -> None:
        """Get number of users of a role

        Example usage
        -------------
        !roleinfo <@role/ID>

        Parameters
        ----------
        role : discord.Role
            "Role to get info of"

        """

        embed = discord.Embed(title="Role Statistics")
        embed.description = f"{len(role.members)} members have role {role.mention}"
        embed.color = role.color
        embed.set_footer(text=f"Requested by {ctx.author}")

        await ctx.message.reply(embed=embed)

    @commands.guild_only()
    @permissions.bot_channel_only_unless_mod()
    @commands.command(name="ping")
    async def ping(self, ctx: context.Context) -> None:
        """Pong

        Example usage
        -------------
        !ping

        """

        b = datetime.datetime.utcnow()
        embed = discord.Embed(
            title=f"Pong!", color=discord.Color.blurple())
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.description = "Latency: testing..."

        # measure time between sending a message and time it is posted
        m = await ctx.message.reply(embed=embed)
        ping = floor((datetime.datetime.utcnow() - b).total_seconds() * 1000)
        await sleep(1)
        embed.description = f"Latency: {ping} ms"
        await m.edit(embed=embed)

    @commands.guild_only()
    @permissions.bot_channel_only_unless_mod()
    @commands.command(name="stats")
    async def stats(self, ctx: context.Context) -> None:
        """Statistics about the bot

        Example usage
        -------------
        !stats

        """

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
    @permissions.bot_channel_only_unless_mod()
    @commands.command(name="serverinfo")
    async def serverinfo(self, ctx: context.Context) -> None:
        """Displays info about the server

        Example usage
        -------------
        !serverinfo

        """

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
    @roleinfo.error
    @stats.error
    @ping.error
    async def info_error(self,  ctx: context.Context, error):
        await ctx.message.delete(delay=5)
        if (isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, permissions.PermissionsFailure)
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.MissingPermissions)
                or isinstance(error, commands.NoPrivateMessage)):
            await ctx.send_error(error)
        else:
            await ctx.send_error("A fatal error occured. Tell <@109705860275539968> about this.")
            traceback.print_exc()


def setup(bot):
    bot.add_cog(Stats(bot))
