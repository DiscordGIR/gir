# !cases
# !warn
# !liftwarn
# !rundown
# !warnpoints
import discord
from discord.ext import commands
class Cases(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="cases")
    async def cases(self, ctx):
        if self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 6):
            results = await self.bot.settings.db.get_with_key('users', 'cases')
            print(results)
def setup(bot):
    bot.add_cog(Cases(bot))