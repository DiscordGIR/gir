# bad words
# spoiler
# invites

import discord
from discord.ext import commands
from cogs.monitors.report import report
import re
# logging
# nsa

class Filters(commands.Cog):
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

        print(guild.filter_excluded_channels)
        print(msg.channel.id)
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

        """
        SPOILER FILTER
        """
        if not self.bot.settings.permissions.hasAtLeast(msg.guild, msg.author, 6):
            if re.search(self.spoiler_filter, msg.content, flags=re.S):
                await msg.delete()
            
            for a in msg.attachments:
                if a.is_spoiler(): 
                    await msg.delete()

        """
        INVITE FILTER
        """
        if not self.bot.settings.permissions.hasAtLeast(msg.guild, msg.author, 6):
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

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        await self.on_message(after)

    @commands.command(name="offlineping")
    async def offlineping(self, ctx, val: bool):
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 6): # must be at least a mod
            raise commands.BadArgument("You need to be a moderator or higher to use that command.")

        cur = await self.bot.settings.user(ctx.author.id)
        cur.offline_report_ping = val
        cur.save()

        if val:
            await ctx.send("You will now be pinged for reports when offline")
        else:
            await ctx.send("You won't be pinged for reports when offline")

    @offlineping.error
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
    bot.add_cog(Filters(bot))