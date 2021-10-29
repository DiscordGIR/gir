from datetime import datetime

from discord.utils import format_dt
from discord.colour import Color
from discord.commands import slash_command
from discord.commands.commands import Option
from discord.embeds import Embed
from discord.ext import commands
from discord.member import Member
from utils.permissions import permissions
from utils.checks import PermissionsFailure, whisper
from utils.config import cfg
from utils.context import GIRContext
from data.services.user_service import user_service

class UserInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.now()

    @whisper()
    @slash_command(guild_ids=[cfg.guild_id], description="Get avatar of another user or yourself.")
    async def avatar(self, ctx: GIRContext, user: Option(Member, description="User to get avatar of", required=False)) -> None:
        if not user:
            user = ctx.user
        embed = Embed(title=f"{user}'s Avatar", color=Color.random())
        embed.set_image(url=user.avatar)
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.respond(embed=embed, ephemeral=ctx.whisper)

    @whisper()
    @slash_command(guild_ids=[cfg.guild_id], description="Get info of another user or yourself.")
    async def userinfo(self, ctx: GIRContext, user: Option(Member, description="User to get info of", required=False)) -> None:
        # TODO when pycord fixes this behavior: handle external members
        
        if user:
            if not permissions.has(ctx.guild, ctx.author, 6):
                raise PermissionsFailure("You do not have permission to access another user's userinfo.")
        else:
            user = ctx.user

        roles = ""
        reversed_roles = user.roles
        reversed_roles.reverse()
        for role in reversed_roles[:-1]:
            roles += role.mention + " "
            
        results = user_service.get_user(user.id)
            
        embed = Embed(title=f"User Information", color=user.color)
        embed.set_author(name=user)
        embed.set_thumbnail(url=user.avatar)
        embed.add_field(name="Username", value=f'{user} ({user.mention})', inline=True)
        embed.add_field(
            name="Level", value=results.level if not results.is_clem else "0", inline=True)
        embed.add_field(
            name="XP", value=results.xp if not results.is_clem else "0/0", inline=True)
        embed.add_field(name="Roles", value=roles if roles else "None", inline=False)
        embed.add_field(name="Join date", value=f"{format_dt(user.joined_at, style='F')} ({format_dt(user.joined_at, style='R')})", inline = True)
        embed.add_field(name="Account creation date", value=f"{format_dt(user.created_at, style='F')} ({format_dt(user.created_at, style='R')})", inline=True)
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.respond(embed=embed, ephemeral=ctx.whisper)

def setup(bot):
    bot.add_cog(UserInfo(bot))