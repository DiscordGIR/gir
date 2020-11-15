# !cases
# !warn
# !liftwarn
# !rundown
# !warnpoints
import discord
from discord.ext import commands
from datetime import datetime

class Cases(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="cases")
    async def cases(self, ctx):
        if self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 6):
            results = await self.bot.settings.db.get_with_key_and_id('users', 'cases', str(ctx.author.id))
            await ctx.send(results)

    @commands.command(name="warn")
    async def warn(self, ctx, user: discord.Member, points: int, *, reason: str = None):
        case = Case(
            _id = str(ctx.author.id),
            _type = "WARN",
            date = datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
            until=str(None),
            modID=str(ctx.author.id),
            modTag = str(ctx.author),
            reason=reason if reason else "No reason",
            punishment=str(points)
        )
        await self.bot.settings.db.append_json("users", "cases", user.id, case.__dict__ )
        results = await self.bot.settings.db.increment_and_get("users", "warnPoints", user.id, case.punishment)
        print(results)
        embed=discord.Embed(title="Warned user")
        embed.set_author(name=user, icon_url=user.avatar_url)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Points", value=points, inline=True)
        embed.add_field(name="Current points", value=results[0]['warnPoints'], inline=True)
        embed.set_footer(text=f"Warned by {ctx.author}")
        await ctx.send(embed=embed)        

    @warn.error
    async def info_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(error)
        if isinstance(error, commands.BadArgument):
            await(ctx.send(error))
        else:
            print(error)
class Case:
    def __init__(self, _id, _type, date, until, modID, modTag, reason, punishment):
        self.id         = _id
        self.type       = _type
        self.date       = date
        self.until      = until
        self.modID      = modID
        self.modTag     = modTag
        self.reason     = reason
        self.punishment = punishment

def setup(bot):
    bot.add_cog(Cases(bot))

