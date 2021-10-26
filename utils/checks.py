from discord.ext import commands

from utils.database import db
from utils.permissions import permissions


def whisper():
    """If the user is not a moderator and the invoked channel is not #bot-commands, send the response to the command ephemerally
    """
    async def predicate(ctx):
        bot_chan = db.guild().channel_botspam
        if not permissions.has(ctx.guild, ctx.author, 5) and ctx.channel.id != bot_chan:
            ctx.whisper = True
        else:
            ctx.whisper = False
        return True
    return commands.check(predicate)
