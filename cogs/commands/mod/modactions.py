import discord
from discord.ext import commands
from cogs.utils.logs import prepare_ban_log, prepare_warn_log, prepare_kick_log
from data.case import Case
import traceback
import typing

class ModActions(commands.Cog):
    def __init__(self, bot):    
        self.bot = bot

    @commands.guild_only()
    @commands.command(name="warn")
    async def warn(self, ctx, user: discord.Member, points: int, *, reason: str = "No reason."):
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 6):
            raise commands.BadArgument("You need to be a moderator or higher to use that command.")
        if points < 1:
            raise commands.BadArgument(message="Points can't be lower than 1.")
        if user.top_role >= ctx.author.top_role:
            raise commands.BadArgument(message=f"{user}'s top role is the same or higher than yours!")
        
        guild = self.bot.settings.guild()
        
        case = Case(
            _id = guild.case_id,
            _type = "WARN",
            mod_id=ctx.author.id,
            mod_tag = str(ctx.author),
            reason=reason,
            punishment_points=points
        )

        await self.bot.settings.inc_caseid()
        await self.bot.settings.add_case(user.id, case)
        await self.bot.settings.inc_points(user.id, points)

        results = await self.bot.settings.user(user.id)
        cur_points = results.warn_points
        log = await prepare_warn_log(ctx, user, case)

        public_chan = discord.utils.get(ctx.guild.channels, id=self.bot.settings.guild().channel_public)
        if public_chan:
            await public_chan.send(embed=log)  

        
        log.add_field(name="Current points", value=cur_points, inline=True)
        await ctx.send(embed=log, delete_after=5)

        if cur_points >= 600:
            await ctx.invoke(self.ban, user=user, reason="600 or more points reached")
        elif cur_points >= 400 and not results.was_warn_kicked:
            await self.bot.settings.set_warn_kicked(user.id)
            
            try:
                await user.send("You were kicked from r/Jailbreak for reaching 400 or more points.", embed=log)
            except Exception:
                pass
            
            await ctx.invoke(self.kick, user=user, reason="400 or more points reached")
        else:
            try:
                await user.send("You were warned in r/Jailbreak.", embed=log)      
            except Exception:
                pass
    
    @commands.guild_only()
    @commands.command(name="kick")
    async def kick(self, ctx, user: discord.Member, *, reason: str = "No reason."):
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 6):
            raise commands.BadArgument("You need to be a moderator or higher to use that command.")
        if user.top_role >= ctx.author.top_role:
            raise commands.BadArgument(message=f"{user}'s top role is the same or higher than yours!")
        
        case = Case(
            _id = self.bot.settings.guild().case_id,
            _type = "KICK",
            mod_id=ctx.author.id,
            mod_tag = str(ctx.author),
            reason=reason,
        )
        await self.bot.settings.inc_caseid()
        await self.bot.settings.add_case(user.id, case)

        log = await prepare_kick_log(ctx, user, case)

        public_chan = discord.utils.get(ctx.guild.channels, id=self.bot.settings.guild().channel_public)
        await public_chan.send(embed=log)
        await ctx.send(embed=log, delete_after=5)
        
        try:
            await user.send("You were kicked from r/Jailbreak", embed=log)
        except Exception:
            pass

        await user.kick(reason=reason)
    
    @commands.guild_only()
    @commands.command(name="ban")
    async def ban(self, ctx, user: typing.Union[discord.Member, int], *, reason: str = "No reason."):
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 6):
            raise commands.BadArgument("You need to be a moderator or higher to use that command.")
        if isinstance(user, discord.Member):
            if user.top_role >= ctx.author.top_role:
                raise commands.BadArgument(message=f"{user}'s top role is the same or higher than yours!")
        
        if isinstance(user, int):
            user = await self.bot.fetch_user(user)
            if user is None:
                raise commands.BadArgument(f"Couldn't find user with ID {user}")

        case = Case(
            _id = self.bot.settings.guild().case_id,
            _type = "BAN",
            mod_id=str(ctx.author.id),
            mod_tag = str(ctx.author),
            reason=reason,
        )
        await self.bot.settings.inc_caseid()
        await self.bot.settings.add_case(user.id, case)

        log = await prepare_ban_log(ctx, user, case)

        public_chan = discord.utils.get(ctx.guild.channels, id=self.bot.settings.guild().channel_public)
        await public_chan.send(embed=log)
        await ctx.send(embed=log)
        
        try:
            await user.send("You were banned from r/Jailbreak", embed=log)
        except Exception:
            pass
        
        if isinstance(user, discord.Member):
            await user.ban(reason=reason)
        else:
            await ctx.guild.ban(discord.Object(id=user.id))

    @commands.guild_only()
    @commands.command(name="purge")
    async def purge(self, ctx, limit: int = 0):
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 6):
            raise commands.BadArgument("You need to be a moderator or higher to use that command.")
        if limit <= 0:
            raise commands.BadArgument("Number of messages to purge must be greater than 0")
        await ctx.channel.purge(limit=limit)
        await ctx.send(f'Purged {limit} messages.', delete_after=5)
    
    @ban.error
    @warn.error
    @purge.error
    @kick.error
    async def info_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await(ctx.send(error, delete_after=5))
        elif isinstance(error, commands.BadArgument):
            await(ctx.send(error, delete_after=5))
        elif isinstance(error, commands.MissingPermissions):
            await(ctx.send(error, delete_after=5))
        elif isinstance(error, commands.NoPrivateMessage):
            await(ctx.send(error, delete_after=5))
        else:
            traceback.print_exc()

def setup(bot):
    bot.add_cog(ModActions(bot))

# !warn
# !lfitwarn
# !kick
# !ban
# !mute
# !clem
# !purge