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
        for i in range (0, 9):
            if self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, i):
                await ctx.send(f"has {i}")
def setup(bot):
    bot.add_cog(Cases(bot))