from asyncio import sleep
from datetime import datetime
from math import floor

from discord.colour import Color
from discord.commands import slash_command
from discord.commands.commands import Option
from discord.embeds import Embed
from discord.ext import commands
from discord.role import Role
from utils.checks import whisper
from utils.config import cfg
from utils.context import GIRContext


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @whisper()
    @slash_command(guild_ids=[cfg.guild_id], description="Pong!")
    async def ping(self, ctx: GIRContext) -> None:
        """Pong

        Example usage
        -------------
        !ping

        """

        embed = Embed(
            title="Pong!", color=Color.blurple())
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

    @whisper()
    @slash_command(guild_ids=[cfg.guild_id], description="Get number of users of a role")
    async def roleinfo(self, ctx: GIRContext, role: Option(Role, description="Role to view info of")) -> None:
        embed = Embed(title="Role Statistics")
        embed.description = f"{len(role.members)} members have role {role.mention}"
        embed.color = role.color
        embed.set_footer(text=f"Requested by {ctx.author}")

        await ctx.respond(embed=embed, ephemeral=ctx.whisper)


def setup(bot):
    bot.add_cog(Stats(bot))
