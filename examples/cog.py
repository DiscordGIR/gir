import traceback

import discord
from discord.ext import commands
import cogs.utils.context as context
import cogs.utils.permission_checks as permissions


"""
Make sure to add the cog to the initial_extensions list
in main.py
"""

class CogName(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="say")
    @commands.guild_only()
    @permissions.mod_and_up()
    async def say(self, ctx: context.Context, *, message: str):
        """Add a description here.

        Example usage
        -------------
        !say hey howdo do!

        Parameters
        ----------
        message : str
            the message to say
        """
        
        await ctx.send_success(message, delete_after=5)

    @say.error
    async def info_error(self, ctx: context.Context, error):
        await ctx.message.delete(delay=5)
        if (isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, permissions.PermissionsFailure)
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.MissingPermissions)
            or isinstance(error, commands.BotMissingPermissions)
            or isinstance(error, commands.MaxConcurrencyReached)
                or isinstance(error, commands.NoPrivateMessage)):
            await ctx.send_error(error)
        else:
            await ctx.send_error("A fatal error occured. Tell <@109705860275539968> about this.")
            traceback.print_exc()


def setup(bot):
    bot.add_cog(CogName(bot))
