from discord.ext import commands

class AppleNews(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, msg):
        if not msg.guild:
            return
        if msg.channel.id != self.bot.settings.guild().channel_applenews:
            return
        if not msg.author.bot:
            return
        if not msg.channel.is_news():
            return
        
        await msg.publish()
    
def setup(bot):
    bot.add_cog(AppleNews(bot))
