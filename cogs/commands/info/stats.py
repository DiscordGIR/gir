from asyncio import sleep
from datetime import datetime
from math import floor

import discord
from discord.commands import context, slash_command
from discord.ext import commands
from utils.checks import whisper
from utils.config import cfg
from utils.context import GIRContext


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @whisper()
    @slash_command(guild_ids=[cfg.guild_id])
    async def ping(self, ctx: GIRContext) -> None:
        """Pong

        Example usage
        -------------
        !ping

        """

        embed = discord.Embed(
            title="Pong!", color=discord.Color.blurple())
        embed.set_thumbnail(url=self.bot.user.display_avatar)
        embed.description = "Latency: testing..."

        # measure time between sending a message and time it is posted
        b = datetime.utcnow()
        await ctx.respond(embed=embed, ephemeral=ctx.whisper)
        ping = floor((datetime.utcnow() - b).total_seconds() * 1000)
        await sleep(1)
        # embed.description = ""
        embed.add_field(name="Message Latency", value=f"`{ping}ms`")
        embed.add_field(name="API Latency", value=f"`{floor(self.bot.latency*1000)}ms`")
        await ctx.edit(embed=embed)


def setup(bot):
    bot.add_cog(Stats(bot))
