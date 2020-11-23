import discord
from discord.ext import commands
from datetime import datetime
from math import floor
import traceback

class UserInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.guild_only()
    @commands.command(name="serverinfo")
    async def userinfo(self, ctx):
        await ctx.message.delete()
        guild = ctx.guild

        embed=discord.Embed(title="Server Information")
        embed.color = discord.Color.blurple()
        embed.set_image(url=guild.icon_url)
        embed.add_field(name="Region", value=guild.region, inline=True)
        embed.add_field(name="Boost Tier", value=guild.premium_tier, inline=True)
        embed.add_field(name="Users", value=guild.member_count, inline=True)
        embed.add_field(name="Channels", value=len(guild.channels) + len(guild.voice_channels), inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
        embed.add_field(name="Created", value=guild.created_at.strftime("%B %d, %Y, %I:%M %p"), inline=True)
        
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)

    @userinfo.error
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
    bot.add_cog(UserInfo(bot))
