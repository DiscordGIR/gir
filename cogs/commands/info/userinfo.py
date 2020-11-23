import discord
from discord.ext import commands
from datetime import datetime
from math import floor
import traceback

class UserInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.guild_only()
    @commands.command(name="userinfo")
    async def userinfo(self, ctx, user:discord.Member=None):
        await ctx.message.delete()
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 6) and ctx.channel.id != 778233669881561088:
            pass
        else:
            if user is None: user = ctx.author

            roles = ""
            for role in user.roles:
                if role != ctx.guild.default_role:
                    roles += role.mention + " "
            results = (await self.bot.settings.user(user.id))
            
            joined = user.joined_at.strftime("%B %d, %Y, %I:%M %p")
            created = user.created_at.strftime("%B %d, %Y, %I:%M %p")

            embed=discord.Embed(title="User Information")
            embed.color = user.color
            embed.set_author(name=user, icon_url=user.avatar_url)
            embed.add_field(name="Username", value=f'{user} ({user.mention})', inline=True)
            embed.add_field(name="Level", value=results.level if not results.is_xp_frozen else "0", inline=True)
            embed.add_field(name="XP", value=results.xp if not results.is_xp_frozen else "0/0", inline=True)
            embed.add_field(name="Roles", value=roles if roles else "None", inline=False)
            embed.add_field(name="Join date", value=f"{joined} UTC", inline=True)
            embed.add_field(name="Account creation date", value=f"{created} UTC", inline=True)
            embed.set_footer(text=f"Requested by {ctx.author}")
            await ctx.send(embed=embed)

    @commands.guild_only()        
    @commands.command(name="xpstats")
    async def xp(self, ctx, user:discord.Member=None):
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 6) and ctx.channel.id != 778233669881561088:
            pass
        else:
            if user is None: user = ctx.author

            results = await self.bot.settings.user(user.id)
            # rank = (await self.bot.settings.db.rank(user.id))[0]["xp_rank"]
            
            embed=discord.Embed(title="Level Statistics")
            embed.color = user.top_role.color
            embed.set_author(name=user, icon_url=user.avatar_url)
            embed.add_field(name="Level", value=results.level if not results.is_xp_frozen else "0", inline=True)
            embed.add_field(name="XP", value=f'{results.xp}/{xp_for_next_level(results.level)}' if not results.is_xp_frozen else "0/0", inline=True)
            # embed.add_field(name="Rank", value=f"{rank}/{ctx.guild.member_count}", inline=True)
            embed.set_footer(text=f"Requested by {ctx.author}")
            await ctx.send(embed=embed)
    
    @commands.guild_only()        
    @commands.command(name="warnpoints")
    async def warnpoints(self, ctx, user:discord.Member):
        await ctx.message.delete()
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 6):
            pass

        results = await self.bot.settings.user(user.id)
        # rank = (await self.bot.settings.db.rank(user.id))[0]["xp_rank"]
        
        embed=discord.Embed(title="Warn Points")
        embed.color = discord.Color.orange()
        embed.set_thumbnail(url=user.avatar_url)
        embed.add_field(name="Member", value=f'{user.mention}\n{user}\n({user.id})', inline=True)
        embed.add_field(name="Warn Points", value=results.warn_points, inline=True)
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)

    @userinfo.error
    @xp.error
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

def xp_for_next_level(next):
    level = 0
    xp = 0

    for i in range(0, next):
        xp = xp + 45 * level * (floor(level / 10) + 1)
        level+= 1

    return xp

def setup(bot):
    bot.add_cog(UserInfo(bot))
