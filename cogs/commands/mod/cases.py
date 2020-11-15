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
    async def warn(self, ctx, user: discord.Member, points: int, *, reason: str = "No reason."):
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 6):
            raise commands.BadArgument("You need to be a moderator or higher to use that command.")
        if points < 1:
            raise commands.BadArgument(message="Points can't be lower than 1.")
        if user.top_role >= ctx.author.top_role:
            raise commands.BadArgument(message=f"{user}'s top role is the same or higher than yours!")
        case = Case(
            _id = str(ctx.author.id),
            _type = "WARN",
            date = datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
            until=str(None),
            modID=str(ctx.author.id),
            modTag = str(ctx.author),
            reason=reason,
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
        
        if results[0]['warnPoints'] >= 400 and not results[0]["warnKicked"]:
            await user.send("You were kicked from r/Jailbreak for reaching 400 or more points.", embed=embed)      
            await user.kick(reason="400 or more points reached")
            await self.bot.settings.db.set_with_key_and_id("users", "warnKicked", user.id, True)
        elif results[0]['warnPoints'] >= 600:
            await user.send("You were banned from r/Jailbreak for reaching 600 or more points.", embed=embed)      
            await user.ban(reason="600 or more points reached.")
        else:
            await user.send("You were warned in r/Jailbreak.", embed=embed)      

    @warn.error
    async def info_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(error)
        if isinstance(error, commands.BadArgument):
            await(ctx.send(error))
        if isinstance(error, commands.MissingPermissions):
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

