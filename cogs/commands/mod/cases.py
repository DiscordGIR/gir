# !cases
# !warn
# !liftwarn
# !rundown
# !warnpoints
import discord
from discord.ext import commands, menus
from datetime import datetime
from data.case import Case
import json
import traceback
import typing

class PaginationSource(menus.GroupByPageSource):
    async def format_page(self, menu, entry):
        user = menu.ctx.args[2]
        embed = discord.Embed(
            title=f'Cases (page {menu.current_page +1}/{self.get_max_pages()})', color=discord.Color.blurple())
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
    async def info_error(self, ctx, error):
        if (isinstance(error, commands.MissingRequiredArgument) 
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.MissingPermissions)
            or isinstance(error, commands.NoPrivateMessage)
            or isinstance(error, commands.CommandInvokeError)):
                await self.bot.send_error(ctx, error)
            # await(ctx.send(error, delete_after=5, allowed_mentions=discord.AllowedMentions(user=False, everyone=False, )))
        else:
            traceback.print_exc()

async def determine_emoji(type):
    emoji_dict = {
        "KICK": "👢",
        "BAN": "❌",
        "UNBAN": "✅",
        "MUTE": "🔇",
        "WARN": "⚠️",
        "UNMUTE": "🔈",
        "LIFTWARN": "⚠️❌"
    }
    return emoji_dict[type]

def setup(bot):
    bot.add_cog(Cases(bot))

