import discord
from discord.ext import commands


class PermissionFailure(commands.CheckFailure):
    def __init__(self, message):
        super(message)

# class PermissionChecks:
#     @staticmethod

class ModsAndBelowMember(commands.Converter):
    async def convert(self, ctx, argument):
        user = await commands.MemberConverter().convert(ctx, argument)
        await self.check_perms(ctx, user)
        return user
    
    @staticmethod
    async def check_perms(ctx, user):
        await check_invokee(ctx, user)
        # must be at least a mod
        if not ctx.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 5):
            raise commands.BadArgument(
                "You do not have permission to use this command.")
        
    
        # return commands.check(predicate)
class ModsAndBelowExternal(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            user = await ModsAndBelowMember().convert(ctx, argument)
        except Exception:
            try:
                argument = int(argument)
                user = await ctx.bot.fetch_user(argument)
            except Exception:
                raise commands.BadArgument("Could not parse argument \"user\".")
            except discord.NotFound:
                raise commands.BadArgument(
                    f"Couldn't find user with ID {argument}")
            
            await ModsAndBelowMember.check_perms(ctx, user)
        
        return user 

async def check_invokee(ctx, user):
    if isinstance(user, discord.Member):
        if user.id == ctx.author.id:
            await ctx.message.add_reaction("🤔")
            raise commands.BadArgument("You can't call that on yourself.")
        
        if user.id == ctx.bot.user.id:
            await ctx.message.add_reaction("🤔")
            raise commands.BadArgument("You can't call that on me :(")
        
        if user:
                if isinstance(user, discord.Member):
                    if user.top_role >= ctx.author.top_role:
                        raise commands.BadArgument(
                            message=f"{user.mention}'s top role is the same or higher than yours!")
