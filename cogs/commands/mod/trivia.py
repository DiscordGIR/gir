from datetime import datetime
import traceback

from discord import member

import cogs.utils.permission_checks as permissions
import cogs.utils.context as context
import discord
from discord.ext import commands, menus


class LeaderboardSource(menus.GroupByPageSource):
    async def format_page(self, menu, entry):
        embed = discord.Embed(
            title=f'Trivia leaderboard', color=discord.Color.blurple())
        for i, user in entry.items:
            member = menu.ctx.guild.get_member(user._id)
            trophy = ''
            if menu.current_page == 0:
                if i == entry.items[0][0]:
                    trophy = ':first_place:'
                    embed.set_thumbnail(url=member.avatar_url)
                elif i == entry.items[1][0]:
                    trophy = ':second_place:'
                elif i == entry.items[2][0]:
                    trophy = ':third_place:'
            
            
            embed.add_field(name=f"#{i+1} - {user.trivia_points} points",
                            value=f"{trophy} {member.mention}", inline=False)
            
        embed.set_footer(
            text=f"Page {menu.current_page +1} of {self.get_max_pages()}")
        return embed


class MenuPages(menus.MenuPages):
    async def update(self, payload):
        if self._can_remove_reactions:
            if payload.event_type == 'REACTION_ADD':
                await self.message.remove_reaction(payload.emoji, payload.member)
            elif payload.event_type == 'REACTION_REMOVE':
                return
        await super().update(payload)


class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_unload(self):
        self.time_updater_loop.cancel()

    @commands.guild_only()
    @commands.max_concurrency(1, per=commands.BucketType.member, wait=False)
    @commands.group()
    async def points(self, ctx: context.Context):
        """
        Manage user points for trivia: !points <action>, choosing from below...
        """

        if ctx.invoked_subcommand is None:
            raise commands.BadArgument("Invalid giveaway subcommand passed. Options: `add`, `remove`, `reset`, `leaderboard`")

    @points.command()
    @permissions.mod_and_up()
    async def add(self, ctx: context.Context, member: discord.Member, amount: int):
        """Give a user trivia points (mod only).

        Parameters
        ----------
        member : discord.Member
            Member to give points to
        amount : int
            Amount of points to give
        """
        
        if amount < 1:
            raise commands.BadArgument("Points must be greater than 1!")
        
        current_points = await ctx.settings.inc_trivia_points(member.id, amount)
        embed = discord.Embed()
        embed.set_author(name=member, icon_url=member.avatar_url)
        embed.color = discord.Color.dark_green()
        embed.description = f"Wow {member.mention}, great moves! Keep it up!\n\n \
            You gained **{amount} points** ({current_points} points in total)"
        embed.set_footer(text=f"Points added by {ctx.author}")
        embed.timestamp = datetime.now()
        
        await ctx.send(embed=embed, delete_after=8)
        await ctx.message.delete(delay=8)
    
    @points.command()
    @permissions.mod_and_up()
    async def remove(self, ctx: context.Context, member: discord.Member, amount: int):
        """Take a user's trivia points (mod only).

        Parameters
        ----------
        member : discord.Member
            Member to take points from
        amount : int
            Amount of points to take
        """
        
        if amount < 1:
            raise commands.BadArgument("Points must be greater than 1!")
        
        current_points = await ctx.settings.inc_trivia_points(member.id, (-1*amount))
        embed = discord.Embed()
        embed.set_author(name=member, icon_url=member.avatar_url)
        embed.color = discord.Color.red()
        embed.description = f"Better luck next time, {member.mention}. \n\n \
            You lost **{amount} points** ({current_points} points in total)"
        embed.set_footer(text=f"Points added by {ctx.author}")
        embed.timestamp = datetime.now()
        
        await ctx.send(embed=embed, delete_after=8)
        await ctx.message.delete(delay=8)
    
    @points.command()
    @permissions.mod_and_up()
    async def reset(self, ctx: context.Context):
        """Reset all points (mod only)
        """
        
        async with ctx.typing():
            members_reset = await ctx.settings.reset_trivia_points()
        
        if not members_reset:
            raise commands.BadArgument("There were no points to reset!")
        
        await ctx.message.delete(delay=5)
        await ctx.send_success(title="Done!", description=f"I reset {members_reset} users' points.", delete_after=5)

    @points.command()
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.channel)
    async def leaderboard(self, ctx: context.Context):
        """Show trivia leaderboard for top 100, ranked highest to lowest.
        """

        results = enumerate(await ctx.settings.trivia_leaderboard())
        # ctx.user_cache = self.user_cache
        results = [ (i, m) for (i, m) in results if ctx.guild.get_member(m._id) is not None and m.trivia_points != 0][0:100]
        if len(results) == 0:
            raise commands.BadArgument("The leaderboard is currently empty.")
        
        menus = MenuPages(source=LeaderboardSource(
            results, key=lambda t: 1, per_page=10), clear_reactions_after=True)
        
        await menus.start(ctx)

    @points.error
    @add.error
    @remove.error
    @reset.error
    @leaderboard.error
    async def info_error(self, ctx: context.Context, error):
        await ctx.message.delete(delay=5)
        if (isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, permissions.PermissionsFailure)
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.MissingPermissions)
            or isinstance(error, commands.CommandInvokeError)
            or isinstance(error, commands.CommandOnCooldown)
            or isinstance(error, commands.BotMissingPermissions)
            or isinstance(error, commands.MaxConcurrencyReached)
                or isinstance(error, commands.NoPrivateMessage)):
            await ctx.send_error(error)
        else:
            await ctx.send_error("A fatal error occured. Tell <@109705860275539968> about this.")
            traceback.print_exc()


def setup(bot):
    bot.add_cog(Giveaway(bot))
