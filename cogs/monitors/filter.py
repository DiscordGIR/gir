import discord
from discord.ext import commands
from cogs.monitors.report import report
import re
import traceback

class FilterMonitor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spoiler_filter = r'\|\|(.*?)\|\|'
        self.invite_filter = r'(?:https?://)?discord(?:(?:app)?\.com/invite|\.gg)/?[a-zA-Z0-9]+/?'
    
    @commands.Cog.listener()
    async def on_message(self, msg):
        guild = self.bot.settings.guild()

        if msg.author.bot:
            return

        if msg.guild.id != self.bot.settings.guild_id:
            return

        if msg.channel.id in guild.filter_excluded_channels:
            return

        """
        BAD WORD FILTER
        """
        delete = False
        for word in guild.filter_words:
            if not self.bot.settings.permissions.hasAtLeast(msg.guild, msg.author, word.bypass):
                if word.word in msg.content:
                    delete = True
                    if word.notify:
                        await report(self.bot, msg, msg.author)
                        break
        if delete:
            await msg.delete()
            return

        """
        INVITE FILTER
        """
        if not self.bot.settings.permissions.hasAtLeast(msg.guild, msg.author, 5):
            invites = re.findall(self.invite_filter, msg.content, flags=re.S)
            if invites:
                whitelist = ["xd", "jb"]
                for invite in invites:
                    splat = invite.split("/")
                    id = splat[-1] or splat[-2]
                    if id.lower() not in whitelist:
                        await msg.delete()
                        await report(self.bot, msg, msg.author)
                        break

        """
        SPOILER FILTER
        """
        if not self.bot.settings.permissions.hasAtLeast(msg.guild, msg.author, 5):
            if re.search(self.spoiler_filter, msg.content, flags=re.S):
                await msg.delete()
                return
            
            for a in msg.attachments:
                if a.is_spoiler(): 
                    await msg.delete()
                    return

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        await self.on_message(after)

    async def info_error(self, ctx, error):
        if (isinstance(error, commands.MissingRequiredArgument) 
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.MissingPermissions)
            or isinstance(error, commands.NoPrivateMessage)):
                await self.bot.send_error(ctx, error)
        else:
            traceback.print_exc()

def setup(bot):
    bot.add_cog(FilterMonitor(bot))