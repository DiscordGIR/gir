import discord
from discord.ext import commands
from datetime import datetime
import json

class UserInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="userinfo")
    async def userinfo(self, ctx, user:discord.Member=None):
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 6) and ctx.channel.id != 778233669881561088:
            pass
        else:
            if user is None: user = ctx.author

            roles = ""
            for role in user.roles:
                if role != ctx.guild.default_role:
                    roles += role.mention + " "
            results = (await self.bot.settings.db.get_with_id("users", user.id))[0]
            
            joined = user.joined_at.strftime("%m/%d/%Y, %H:%M:%S")
            created = user.created_at.strftime("%m/%d/%Y, %H:%M:%S")

            embed=discord.Embed(title="User Information")
            embed.color = user.top_role.color
            embed.set_author(name=user, icon_url=user.avatar_url)
            embed.add_field(name="Username", value=f'{user} ({user.mention})', inline=True)
            embed.add_field(name="Level", value=results["level"] if not results["xpFrozen"] else "0", inline=True)
            embed.add_field(name="XP", value=results["xp"] if not results["xpFrozen"] else "0/0", inline=True)
            embed.add_field(name="Roles", value=roles if roles else "None", inline=False)
            embed.add_field(name="Join date", value=f"{joined} UTC", inline=True)
            embed.add_field(name="Account creation date", value=f"{created} UTC", inline=True)
            embed.set_footer(text=f"Requested by {ctx.author}")
            await ctx.send(embed=embed)
def setup(bot):
    bot.add_cog(UserInfo(bot))
