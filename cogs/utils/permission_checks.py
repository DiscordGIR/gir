import discord
from discord.ext import commands


class ModsAndAboveMember(commands.Converter):
    async def convert(self, ctx, argument):
        user = await commands.MemberConverter().convert(ctx, argument)
        await self.check_perms(ctx, user)
        return user
    
    @staticmethod
    async def check_perms(ctx, user):
        await check_invokee(ctx, user)

class ModsAndAboveExternal(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            user = await ModsAndAboveMember().convert(ctx, argument)
        except Exception:
            try:
                argument = int(argument)
                user = await ctx.bot.fetch_user(argument)
            except Exception:
                raise commands.BadArgument("Could not parse argument \"user\".")
            except discord.NotFound:
                raise commands.BadArgument(
                    f"Couldn't find user with ID {argument}")
            
            await ModsAndAboveMember.check_perms(ctx, user)
        
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

def genius_and_up():
    async def predicate(ctx):
        if not ctx.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 4):
            raise commands.BadArgument(
                "You do not have permission to use this command.")
        
        return True
    return commands.check(predicate)


def mod_and_up():
    async def predicate(ctx):
        if not ctx.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 5):
            raise commands.BadArgument(
                "You do not have permission to use this command.")
        
        return True
    return commands.check(predicate)


def admin_and_up():
    async def predicate(ctx):
        if not ctx.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 6):
            raise commands.BadArgument(
                "You do not have permission to use this command.")
        
        return True
    return commands.check(predicate)