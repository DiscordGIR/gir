import discord
from discord.ext import commands
from datetime import datetime
import json

class UserInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="userinfo")
    async def userinfo(self, ctx, user:discord.Member):
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 6) and ctx.channel.id != 778233669881561088:
            pass
        else:
            roles = ""
            for role in user.roles:
                if role != ctx.guild.default_role:
                    roles += role.mention + " "
            embed=discord.Embed(title="User Information")
            embed.set_author(name=user, icon_url=user.avatar_url)
            embed.add_field(name="Username", value=f'{user} ({user.mention})', inline=True)
            embed.add_field(name="Level", value="something idk yet", inline=True)
            embed.add_field(name="XP", value="something idk yet", inline=True)
            embed.add_field(name="Roles", value=roles if roles else "None", inline=False)
            embed.add_field(name="Joined", value="idk yet", inline=True)
            embed.add_field(name="Created", value="idk yet", inline=True)
            # embed.set_footer(text=f"user.i | Warned by {ctx.author}")
            await ctx.send(embed=embed)
def setup(bot):
    bot.add_cog(UserInfo(bot))
