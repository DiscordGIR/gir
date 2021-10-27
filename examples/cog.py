from discord.commands import Option, slash_command
from discord.ext import commands
from utils.checks import whisper
from utils.config import cfg
from utils.context import GIRContext

"""
Make sure to add the cog to the initial_extensions list
in main.py
"""

class CogName(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @whisper()
    @slash_command(guild_ids=[cfg.guild_id], description="Make bot say something")
    async def say(self, ctx: GIRContext, *, message: Option(str, description="Message to send")):
        await ctx.respond(message, ephemeral=ctx.whisper)


def setup(bot):
    bot.add_cog(CogName(bot))
