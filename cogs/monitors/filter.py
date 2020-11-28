# bad words
# spoiler
# invites

import discord
from discord.ext import commands
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
        if msg.author.bot:
            return

        if msg.guild.id != self.bot.settings.guild_id:
            return

        # if self.bot.settings.permissions.hasAtLeast(msg.guild, msg.author, 6):
        #     return

        """
        SPOILER FILTER
        """
        if re.search(self.spoiler_filter, msg.content, flags=re.S):
            await msg.delete()
        
        for a in msg.attachments:
            if a.is_spoiler(): 
                await msg.delete()

        """
        INVITE FILTER
        """
        invites = re.findall(self.invite_filter, msg.content, flags=re.S)
        if invites:
            whitelist = ["xd", "jb"]
            for invite in invites:
                splat = invite.split("/")
                id = splat[-1] or splat[-2]
                if id.lower() not in whitelist:
                    await msg.delete()
                    break

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        await self.on_message(after)

def setup(bot):
    bot.add_cog(Filters(bot))