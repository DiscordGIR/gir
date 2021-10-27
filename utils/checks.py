from discord.ext import commands
from utils.context import GIRContext

from utils.database import db
from utils.permissions import permissions


class PermissionsFailure(commands.BadArgument):
    def __init__(self, message):
        super().__init__(message)


def whisper():
    """If the user is not a moderator and the invoked channel is not #bot-commands, send the response to the command ephemerally
    """
    async def predicate(ctx: GIRContext):
        bot_chan = db.guild().channel_botspam
        if not permissions.has(ctx.guild, ctx.author, 5) and ctx.channel.id != bot_chan:
            ctx.whisper = True
        else:
            ctx.whisper = False
        return True
    return commands.check(predicate)

def memplus_and_up():
    async def predicate(ctx: GIRContext):
        if not permissions.has(ctx.guild, ctx.author, 1):
            raise PermissionsFailure("You do not have permission to use this command.")
        
        return True
    return commands.check(predicate)

def mempro_and_up():
    async def predicate(ctx: GIRContext):
        if not permissions.has(ctx.guild, ctx.author, 2):
            raise PermissionsFailure("You do not have permission to use this command.")
        
        return True
    return commands.check(predicate)

def memed_and_up():
    async def predicate(ctx: GIRContext):
        if not permissions.has(ctx.guild, ctx.author, 3):
            raise PermissionsFailure("You do not have permission to use this command.")
        
        return True
    return commands.check(predicate)

def genius_and_up():
    async def predicate(ctx: GIRContext):
        if not permissions.has(ctx.guild, ctx.author, 4):
            raise PermissionsFailure("You do not have permission to use this command.")
        
        return True
    return commands.check(predicate)

####################
# Staff Roles
####################

def submod_or_admin_and_up():
    async def predicate(ctx: GIRContext):
        db = ctx.bot.settings.guild()
        submod = ctx.guild.get_role(db.role_sub_mod)
        if not submod:
            return

        if not (permissions.has(ctx.guild, ctx.author, 6) or submod in ctx.author.roles):
            raise commands.BadArgument(
                "You do not have permission to use this command.")

        return True
    return commands.check(predicate)

def genius_or_submod_and_up():
    async def predicate(ctx: GIRContext):
        db = ctx.bot.settings.guild()
        submod = ctx.guild.get_role(db.role_sub_mod)
        if not submod:
            return

        if not (permissions.has(ctx.guild, ctx.author, 4) or submod in ctx.author.roles):
            raise commands.BadArgument(
                "You do not have permission to use this command.")

        return True
    return commands.check(predicate)

def mod_and_up():
    async def predicate(ctx: GIRContext):
        if not permissions.has(ctx.guild, ctx.author, 5):
            raise PermissionsFailure(
                "You do not have permission to use this command.")
        
        return True
    return commands.check(predicate)

def admin_and_up():
    async def predicate(ctx: GIRContext):
        if not permissions.has(ctx.guild, ctx.author, 6):
            raise PermissionsFailure(
                "You do not have permission to use this command.")
        
        return True
    return commands.check(predicate)

####################
# Other
####################

def guild_owner_and_up():
    async def predicate(ctx: GIRContext):
        if not permissions.has(ctx.guild, ctx.author, 7):
            raise PermissionsFailure(
                "You do not have permission to use this command.")
        
        return True
    return commands.check(predicate)

def bot_owner_and_up():
    async def predicate(ctx: GIRContext):
        if not permissions.has(ctx.guild, ctx.author, 9):
            raise PermissionsFailure(
                "You do not have permission to use this command.")
        
        return True
    return commands.check(predicate)

def ensure_invokee_role_lower_than_bot():
    async def predicate(ctx: GIRContext):
        if ctx.me.top_role < ctx.author.top_role:
            raise PermissionsFailure(
                f"Your top role is higher than mine. I can't change your nickname :(")
        
        return True
    return commands.check(predicate)