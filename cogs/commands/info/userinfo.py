import traceback
import typing
from math import floor

import cogs.utils.permission_checks as permissions
import cogs.utils.context as context
import discord
from discord.ext import commands, menus


class LeaderboardSource(menus.GroupByPageSource):
    async def format_page(self, menu, entry):
        embed = discord.Embed(
            title=f'Leaderboard', color=discord.Color.blurple())
        for i, user in entry.items:
            member = menu.ctx.guild.get_member(user._id)
            trophy = ''
            if menu.current_page == 0:
                if i == entry.items[0][0]:
                    trophy = ':first_place:'
                    embed.set_thumbnail(url=member.avatar_url)
                if i == entry.items[1][0]:
                    trophy = ':second_place:'
                if i == entry.items[2][0]:
                    trophy = ':third_place:'
            
            
            embed.add_field(name=f"#{i+1} - Level {user.level}",
                            value=f"{trophy} {member.mention}", inline=False)
            
        embed.set_footer(
            text=f"Page {menu.current_page +1} of {self.get_max_pages()}")
        return embed


class CasesSource(menus.GroupByPageSource):
    async def format_page(self, menu, entry):
        pun_map = {
            "KICK": "Kicked",
            "BAN": "Banned",
            "CLEM": "Clemmed",
            "UNBAN": "Unbanned",
            "MUTE": "Duration",
            "REMOVEPOINTS": "Points removed"
        }

        user = menu.ctx.args[2] or menu.ctx.author
        u = await menu.ctx.bot.settings.user(user.id)
        embed = discord.Embed(
            title=f'Cases - {u.warn_points} warn points', color=discord.Color.blurple())
        embed.set_author(name=user, icon_url=user.avatar_url)
        for case in entry.items:
            timestamp = case.date.strftime("%B %d, %Y, %I:%M %p")
            if case._type == "WARN" or case._type == "LIFTWARN":
                if case.lifted:
                    embed.add_field(name=f'{await determine_emoji(case._type)} Case #{case._id} [LIFTED]',
                                    value=f'**Points**: {case.punishment}\n**Reason**: {case.reason}\n**Lifted by**: {case.lifted_by_tag}\n**Lift reason**: {case.lifted_reason}\n**Warned on**: {timestamp}', inline=True)
                elif case._type == "LIFTWARN":
                    embed.add_field(name=f'{await determine_emoji(case._type)} Case #{case._id} [LIFTED (legacy)]',
                                    value=f'**Points**: {case.punishment}\n**Reason**: {case.reason}\n**Moderator**: {case.mod_tag}\n**Warned on**: {timestamp} UTC', inline=True)
                else:
                    embed.add_field(name=f'{await determine_emoji(case._type)} Case #{case._id}',
                                    value=f'**Points**: {case.punishment}\n**Reason**: {case.reason}\n**Moderator**: {case.mod_tag}\n**Warned on**: {timestamp} UTC', inline=True)
            elif case._type == "MUTE" or case._type == "REMOVEPOINTS":
                embed.add_field(name=f'{await determine_emoji(case._type)} Case #{case._id}',
                                value=f'**{pun_map[case._type]}**: {case.punishment}\n**Reason**: {case.reason}\n**Moderator**: {case.mod_tag}\n**Time**: {timestamp} UTC', inline=True)
            elif case._type in pun_map:
                embed.add_field(name=f'{await determine_emoji(case._type)} Case #{case._id}',
                                value=f'**Reason**: {case.reason}\n**Moderator**: {case.mod_tag}\n**{pun_map[case._type]} on**: {timestamp} UTC', inline=True)
            else:
                embed.add_field(name=f'{await determine_emoji(case._type)} Case #{case._id}',
                                value=f'**Reason**: {case.reason}\n**Moderator**: {case.mod_tag}\n**Time**: {timestamp} UTC', inline=True)
        embed.set_footer(
            text=f"Page {menu.current_page +1} of {self.get_max_pages()} - newest cases first")
        return embed


class MenuPages(menus.MenuPages):
    async def update(self, payload):
        if self._can_remove_reactions:
            if payload.event_type == 'REACTION_ADD':
                await self.message.remove_reaction(payload.emoji, payload.member)
            elif payload.event_type == 'REACTION_REMOVE':
                return
        await super().update(payload)


class UserInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.guild_only()
    @commands.command(name="userinfo", aliases=["info"])
    async def userinfo(self, ctx: context.Context, user: typing.Union[discord.Member, int] = None) -> None:
        """Get information about a user (join/creation date, xp, etc.), defaults to command invoker.

        Example usage:
        --------------
        `!userinfo <@user/ID (optional)>`

        Parameters
        ----------
        user : discord.Member, optional
            User to get info about, by default the author of command, by default None
        """

        if user is None:
            user = ctx.author

        is_mod = ctx.permissions.hasAtLeast(ctx.guild, ctx.author, 5)

        if isinstance(user, int):
            if not is_mod:
                raise commands.BadArgument("You do not have permission to use this command.")
            try:
                user = await self.bot.fetch_user(user)
            except discord.NotFound:
                raise commands.BadArgument(
                    f"Couldn't find user with ID {user}")

        if not is_mod and user.id != ctx.author.id:
            await ctx.message.delete()
            raise commands.BadArgument(
                "You do not have permission to use this command.")

        bot_chan = ctx.settings.guild().channel_botspam
        if not is_mod and ctx.channel.id != bot_chan:
            raise commands.BadArgument(
                f"Command only allowed in <#{bot_chan}>")

        roles = ""

        if isinstance(user, discord.Member):
            reversed_roles = user.roles
            reversed_roles.reverse()

            for role in reversed_roles:
                if role != ctx.guild.default_role:
                    roles += role.mention + " "

            joined = user.joined_at.strftime("%B %d, %Y, %I:%M %p") + " UTC"
        else:
            roles = "No roles."
            joined = f"User not in {ctx.guild.name}."

        results = (await ctx.settings.user(user.id))

        created = user.created_at.strftime("%B %d, %Y, %I:%M %p") + " UTC"

        embed = discord.Embed(title="User Information")
        embed.color = user.color
        embed.set_author(name=user)
        embed.set_thumbnail(url=user.avatar_url)
        embed.add_field(name="Username",
                        value=f'{user} ({user.mention})', inline=True)
        embed.add_field(
            name="Level", value=results.level if not results.is_clem else "0", inline=True)
        embed.add_field(
            name="XP", value=results.xp if not results.is_clem else "0/0", inline=True)
        embed.add_field(
            name="Roles", value=roles if roles else "None", inline=False)
        embed.add_field(name="Join date", value=joined, inline=True)
        embed.add_field(name="Account creation date",
                        value=created, inline=True)
        embed.set_footer(text=f"Requested by {ctx.author}")

        await ctx.message.reply(embed=embed)

    @commands.guild_only()
    @permissions.bot_channel_only_unless_mod()
    @commands.command(name="xpstats", aliases=["xp"])
    async def xp(self, ctx: context.Context, user: discord.Member = None):
        """Show your or another user's XP

        Example usage:
        --------------
        `!xp <@user/ID (optional)`

        Parameters
        ----------
        user : discord.Member, optional
            User to get XP of, by default None

        """

        if user is None:
            user = ctx.author

        results = await ctx.settings.user(user.id)

        embed = discord.Embed(title="Level Statistics")
        embed.color = user.top_role.color
        embed.set_author(name=user, icon_url=user.avatar_url)
        embed.add_field(
            name="Level", value=results.level if not results.is_clem else "0", inline=True)
        embed.add_field(
            name="XP", value=f'{results.xp}/{xp_for_next_level(results.level)}' if not results.is_clem else "0/0", inline=True)
        rank, overall = await ctx.settings.leaderboard_rank(results.xp) 
        embed.add_field(name="Rank", value=f"{rank}/{overall}" if not results.is_clem else f"{overall}/{overall}", inline=True)
        embed.set_footer(text=f"Requested by {ctx.author}")

        await ctx.message.reply(embed=embed)

    @commands.guild_only()
    @permissions.bot_channel_only_unless_mod()
    @commands.command(name="xptop", aliases=["leaderboard"])
    async def xptop(self, ctx: context.Context):
        """Show XP leaderboard for top 100, ranked highest to lowest.

        Example usage:
        --------------
        `!xptop`

        """

        results = enumerate(await ctx.settings.leaderboard())
        # ctx.user_cache = self.user_cache
        results = [ (i, m) for (i, m) in results if ctx.guild.get_member(m._id) is not None][0:100]
        menus = MenuPages(source=LeaderboardSource(
            results, key=lambda t: 1, per_page=10), clear_reactions_after=True)

        await menus.start(ctx)

    @commands.guild_only()
    @permissions.bot_channel_only_unless_mod()
    @commands.command(name="warnpoints", aliases=["wp", "wap"])
    async def warnpoints(self, ctx: context.Context, user: discord.Member = None):
        """Show a user's warnpoints (mod only)

        Example usage:
        --------------
        `!warnpoints <@user/ID>`

        Parameters
        ----------
        user : discord.Member
            User whose warnpoints to show

        """

        user = user or ctx.author

        if not ctx.permissions.hasAtLeast(ctx.guild, ctx.author, 5) and user.id != ctx.author.id:
            raise commands.BadArgument(
                f"You don't have permissions to check others' warnpoints.")

        results = await ctx.settings.user(user.id)

        embed = discord.Embed(title="Warn Points")
        embed.color = discord.Color.orange()
        embed.set_thumbnail(url=user.avatar_url)
        embed.add_field(
            name="Member", value=f'{user.mention}\n{user}\n({user.id})', inline=True)
        embed.add_field(name="Warn Points",
                        value=results.warn_points, inline=True)
        embed.set_footer(text=f"Requested by {ctx.author}")

        await ctx.message.reply(embed=embed)

    @commands.guild_only()
    @commands.command(name="cases")
    async def cases(self, ctx: context.Context, user: typing.Union[discord.Member, int] = None):
        """Show list of cases of a user (mod only)

        Example usage:
        --------------
        `!cases <@user/ID>`

        Parameters
        ----------
        user : typing.Union[discord.Member,int]
            User we want to get cases of, doesn't have to be in guild

        """

        if user is None:
            user = ctx.author
            ctx.args[2] = user

        bot_chan = ctx.settings.guild().channel_botspam
        if not ctx.permissions.hasAtLeast(ctx.guild, ctx.author, 5) and ctx.channel.id != bot_chan:
            raise commands.BadArgument(
                f"Command only allowed in <#{bot_chan}>")

        if not isinstance(user, int):
            if not ctx.permissions.hasAtLeast(ctx.guild, ctx.author, 5) and user.id != ctx.author.id:
                raise commands.BadArgument(
                    f"You don't have permissions to check others' cases.")
        else:
            if not ctx.permissions.hasAtLeast(ctx.guild, ctx.author, 5):
                raise commands.BadArgument(
                    f"You don't have permissions to check others' cases.")

        if isinstance(user, int):
            try:
                user = await self.bot.fetch_user(user)
            except Exception:
                raise commands.BadArgument(
                    f"Couldn't find user with ID {user}")
            ctx.args[2] = user

        results = await ctx.settings.cases(user.id)
        if len(results.cases) == 0:
            if isinstance(user, int):
                raise commands.BadArgument(
                    f'User with ID {user.id} had no cases.')
            else:
                raise commands.BadArgument(f'{user.mention} had no cases.')
        cases = [case for case in results.cases if case._type != "UNMUTE"]
        cases.reverse()

        menus = MenuPages(source=CasesSource(
            cases, key=lambda t: 1, per_page=9), clear_reactions_after=True)
        await ctx.message.delete()
        await menus.start(ctx)

    @cases.error
    @userinfo.error
    @warnpoints.error
    @xp.error
    @xptop.error
    async def info_error(self, ctx: context.Context, error):
        await ctx.message.delete(delay=5)
        if (isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, permissions.PermissionsFailure)
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.MissingPermissions)
                or isinstance(error, commands.NoPrivateMessage)):
            await ctx.send_error(error)
        else:
            await ctx.send_error("A fatal error occured. Tell <@109705860275539968> about this.")
            traceback.print_exc()


def xp_for_next_level(next):
    level = 0
    xp = 0

    for _ in range(0, next):
        xp = xp + 45 * level * (floor(level / 10) + 1)
        level += 1

    return xp


async def determine_emoji(type):
    emoji_dict = {
        "KICK": "👢",
        "BAN": "❌",
        "UNBAN": "✅",
        "MUTE": "🔇",
        "WARN": "⚠️",
        "UNMUTE": "🔈",
        "LIFTWARN": "⚠️",
        "REMOVEPOINTS": "⬇️",
        "CLEM": "👎"
    }
    return emoji_dict[type]


def setup(bot):
    bot.add_cog(UserInfo(bot))
