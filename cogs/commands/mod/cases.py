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
            _id = str((await self.bot.settings.db.increment_and_get("clientStorage", "caseID", ctx.guild.default_role.id, 1))[0]["caseID"]),
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
        cur_points = results[0]['warnPoints']
        log = await self.prepare_log(ctx, user, case)

        public_chan = discord.utils.get(ctx.guild.channels, id=self.bot.settings.channels.public)
        await public_chan.send(embed=log)  

        
        log.add_field(name="Current points", value=cur_points, inline=True)
        await ctx.send(embed=log)

        if cur_points >= 400 and not results[0]["warnKicked"]:
            await self.bot.settings.db.set_with_key_and_id("users", "warnKicked", user.id, True)
            await user.send("You were kicked from r/Jailbreak for reaching 400 or more points.", embed=log)      
            await user.kick(reason="400 or more points reached")
        elif cur_points >= 600:
            await user.send("You were banned from r/Jailbreak for reaching 600 or more points.", embed=log)      
            await user.ban(reason="600 or more points reached.")
        else:
            await user.send("You were warned in r/Jailbreak.", embed=log)      

    # @warn.error
    # async def info_error(self, ctx, error):
    #     if isinstance(error, commands.MissingRequiredArgument):
    #         await ctx.send(error)
    #     if isinstance(error, commands.BadArgument):
    #         await(ctx.send(error))
    #     if isinstance(error, commands.MissingPermissions):
    #         await(ctx.send(error))
    #     else:
    #         print(error)

    async def prepare_log(self, ctx, user, case):
        embed=discord.Embed(title="Member warned")
        embed.set_author(name=user, icon_url=user.avatar_url)
        embed.add_field(name="Member", value=f'{user} ({user.mention})', inline=True)
        embed.add_field(name="Mod", value=f'{ctx.author} ({ctx.author.mention})', inline=True)
        embed.add_field(name="Increase", value=case.punishment, inline=True)
        embed.add_field(name="Reason", value=case.reason, inline=True)
        embed.set_footer(text=f"Case #{case.id} | Warned by {ctx.author}")
        return embed
    
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

