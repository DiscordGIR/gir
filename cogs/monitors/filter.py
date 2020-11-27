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
    
    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot:
            return

        if msg.guild.id != self.bot.settings.guild_id:
            return

        if self.bot.settings.permissions.hasAtLeast(msg.guild, msg.author, 6):
            return

        if re.search(self.spoiler_filter, msg.content, flags=re.S):
            await msg.delete()
        
        for a in msg.attachments:
            if a.is_spoiler(): 
                await msg.delete()

def setup(bot):
    bot.add_cog(Filters(bot))