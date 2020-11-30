import discord
from discord.ext import commands
from discord.ext import menus
from datetime import datetime
from math import floor
from data.case import Case
import typing
import traceback

class LeaderboardSource(menus.GroupByPageSource):
    async def format_page(self, menu, entry):
        embed = discord.Embed(
            title=f'Leaderboard', color=discord.Color.blurple())
        # embed.set_author(name=user, icon_url=user.avatar_url)
        for i, user in entry.items:
            trophy = ''
            if i == 0:
                trophy = ':first_place:'
                # embed.set_thumbnail(url=.user.avatar_url)
            if i == 1:
                trophy = ':second_place:'
            if i == 2:
                trophy = ':third_place:'
            embed.add_field(name=f"#{i+1} - Level {user.level}", value=f"{trophy} <@{user._id}>", inline=False)
        embed.set_footer(text=f"Page {menu.current_page +1} of {self.get_max_pages()}")
        return embed

class CasesSource(menus.GroupByPageSource):
    async def format_page(self, menu, entry):
        user = menu.ctx.args[2]
        embed = discord.Embed(
            title=f'Cases', color=discord.Color.blurple())
        embed.set_author(name=user, icon_url=user.avatar_url)
        for case in entry.items:
            timestamp=case.date.strftime("%B %d, %Y, %I:%M %p")
            if case._type == "WARN":
                if case.lifted:
                    embed.add_field(name=f'{await determine_emoji(case._type)} Case #{case._id} [LIFTED]', 
                        value=f'**Points**: {case.punishment}\n**Reason**: {case.reason}\n**Lifted by**: {case.lifted_by_tag}\n**Lift reason**: {case.lifted_reason}\n**Warned on**: {case.date}', inline=True)
                else:
                    embed.add_field(name=f'{await determine_emoji(case._type)} Case #{case._id}', 
                        value=f'**Points**: {case.punishment}\n**Reason**: {case.reason}\n**Moderator**: {case.mod_tag}\n**Time**: {timestamp} UTC', inline=True)
            elif case._type == "MUTE":
                embed.add_field(name=f'{await determine_emoji(case._type)} Case #{case._id}', 
                    value=f'**Duration**: {case.punishment}\n**Reason**: {case.reason}\n**Moderator**: {case.mod_tag}\n**Time**: {timestamp} UTC', inline=True)
            else:
                embed.add_field(name=f'{await determine_emoji(case._type)} Case #{case._id}', 
                    value=f'**Reason**: {case.reason}\n**Moderator**: {case.mod_tag}\n**Time**: {timestamp} UTC', inline=True)
        embed.set_footer(text=f"Page {menu.current_page +1} of {self.get_max_pages()}")
        return embed

class MenuPages(menus.MenuPages):
    async def update(self, payload):
        if self._can_remove_reactions:
            if payload.event_type == 'REACTION_ADD':
                await self.bot.http.remove_reaction(
                    payload.channel_id, payload.message_id,
                    discord.Message._emoji_reaction(
                        payload.emoji), payload.member.id
                )
            elif payload.event_type == 'REACTION_REMOVE':
                return
        await super().update(payload)


class UserInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.guild_only()
    @commands.command(name="userinfo")
    async def userinfo(self, ctx, user:discord.Member=None):
        # await ctx.message.delete()
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
            # await ctx.send(embed=embed)
            await ctx.message.reply(embed=embed)
    
    @commands.guild_only()        
    @commands.command(name="xpstats", aliases=["xp"])
    async def xp(self, ctx, user:discord.Member=None):
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 6) and ctx.channel.id != 778233669881561088:
            raise commands.BadArgument("Please use #bot-commands")
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
            # await ctx.send(embed=embed)
            await ctx.message.reply(embed=embed)

    @commands.guild_only()
    @commands.command(name="xptop", aliases=["leaderboard"])
    async def xptop(self, ctx):
        results = await self.bot.settings.leaderboard()
        menus = MenuPages(source=LeaderboardSource(
            enumerate(results), key=lambda t: 1, per_page=10), clear_reactions_after=True)

        await menus.start(ctx)

    @commands.guild_only()        
    @commands.command(name="warnpoints")
    async def warnpoints(self, ctx, user:discord.Member):
        # await ctx.message.delete()
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
        # await ctx.send(embed=embed)
        await ctx.message.reply(embed=embed)
    
    @commands.command(name="cases")
    async def cases(self, ctx, user:typing.Union[discord.Member,int]):
        await ctx.message.delete()
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 6):
            raise commands.BadArgument("You need to be a moderator or higher to use that command.")
        
        if isinstance(user, int):
            user = await self.bot.fetch_user(user)
            if user is None:
                raise commands.BadArgument(f"Couldn't find user with ID {user}")
            ctx.args[2] = user

        results = await self.bot.settings.cases(user.id)
        if len(results.cases) == 0:
            if isinstance(user, int):
                raise commands.BadArgument(f'User with ID {user.id} had no cases.')
            else:
                raise commands.BadArgument(f'{user.mention} had no cases.')
        cases = [case for case in results.cases if case._type != "UNMUTE"]

        menus = MenuPages(source=PaginationSource(
            cases, key=lambda t: 1, per_page=9), clear_reactions_after=True)

        await menus.start(ctx)

    @cases.error
    @userinfo.error
    @xp.error
    async def info_error(self, ctx, error):
        if (isinstance(error, commands.MissingRequiredArgument) 
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.MissingPermissions)
            or isinstance(error, commands.NoPrivateMessage)):
                await self.bot.send_error(ctx, error)
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
