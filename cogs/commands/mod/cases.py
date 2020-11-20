# !cases
# !warn
# !liftwarn
# !rundown
# !warnpoints
import discord
from discord.ext import commands, menus
from datetime import datetime
from cogs.utils.case import Case
import json
import traceback
import typing

class PaginationSource(menus.GroupByPageSource):
    async def format_page(self, menu, entry):
        user = menu.ctx.args[2]
        embed = discord.Embed(
            title=f'Cases {menu.current_page +1}/{self.get_max_pages()}', color=discord.Color.blurple())
        embed.set_author(name=user, icon_url=user.avatar_url)
        for result in entry.items:        
            extra = ""
            if result["type"] == "WARN":
                extra = f'**Points**: {result["punishment"]}\n'
            print(result["date"])
            timestamp=datetime.utcfromtimestamp(result["date"]/1000).strftime("%B %d, %Y, %I:%M %p")
            embed.add_field(name=f'{await determine_emoji(result["type"])} Case #{result["id"]}', 
                value=f'{extra} **Reason**: {result["reason"]}\n**Moderator**: {result["modTag"]}\n**Time**: {timestamp} UTC', inline=True)
        
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
        
class Cases(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="cases")
    async def cases(self, ctx, user:typing.Union[discord.Member,int]):
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 6):
            raise commands.BadArgument("You need to be a moderator or higher to use that command.")
        
        if isinstance(user, int):
            user = await self.bot.fetch_user(user)
            if user is None:
                raise commands.BadArgument(f"Couldn't find user with ID {user}")
            ctx.args[2] = user

        results = await self.bot.settings.db.get_with_key_and_id('users', 'cases', user.id)
        if len(results) == 0:
            raise commands.BadArgument(f'User with ID {user} had no cases.')
        results = results[0]['cases']
        results = [json.loads(case) for case in results]
        results = [case for case in results if case["type"] != "UNMUTE"]

        menus = MenuPages(source=PaginationSource(
            results, key=lambda t: 1, per_page=9), clear_reactions_after=True)

        await menus.start(ctx)
    
    @cases.error
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

async def determine_emoji(type):
    emoji_dict = {
        "KICK": "👢",
        "BAN": "❌",
        "MUTE": "🔇",
        "WARN": "⚠️",
        "UNMUTE": "🔈",
    }
    return emoji_dict[type]

def setup(bot):
    bot.add_cog(Cases(bot))

