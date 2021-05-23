import discord
from discord.ext import commands

class PermissionChecks:
    @staticmethod
    def mods_and_up():
        async def predicate(ctx):
            if hasattr(ctx, 'user'):
                user = ctx.user
            elif hasattr(ctx, 'member'):
                user = ctx.member
            else:
                return False
            
            if isinstance(user, discord.Member):
                if user.id == ctx.author.id:
                    await ctx.message.add_reaction("🤔")
                    raise commands.BadArgument("You can't call that on yourself.")
                if user.id == ctx.bot.user.id:
                    await ctx.message.add_reaction("🤔")
                    raise commands.BadArgument("You can't call that on me :(")

            # must be at least a mod
            if not ctx.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 5):
                raise commands.BadArgument(
                    "You do not have permission to use this command.")
            if user:
                if isinstance(user, discord.Member):
                    if user.top_role >= ctx.author.top_role:
                        raise commands.BadArgument(
                            message=f"{user.mention}'s top role is the same or higher than yours!")

            return True
            
        return commands.check(predicate)
    