# !cases
# !warn
# !liftwarn
# !rundown
# !warnpoints
import discord
from discord.ext import commands
from datetime import datetime
from cogs.utils.case import Case
import json
class Cases(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="cases")
    async def cases(self, ctx, user:discord.Member):
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 6):
            pass
        else:
            results = await self.bot.settings.db.get_with_key_and_id('users', 'cases', str(user.id))
            embed=discord.Embed(title="Cases")
            embed.set_author(name=user, icon_url=user.avatar_url)
            results = ((results[0]['cases']))
            # results = json.loads([results[0])
            for result in results:
                result = json.loads(result)
                print(result)
                
                extra = ""
                if result["type"] == "UNMUTE":
                    continue
                elif result["type"] == "WARN":
                    extra = f'**Points**: {result["punishment"]}\n'
                
                timestamp=datetime.utcfromtimestamp(result["date"]/1000).strftime("%Y-%m-%d %H:%M:%S")
                embed.add_field(name=f'{await self.determine_emoji(result["type"])} Case #{result["id"]}', 
                    value=f'{extra} **Reason**: {result["reason"]}\n**Moderator**: {result["modTag"]}\n**Time**: {timestamp}', inline=False)
            await ctx.send(embed=embed)
    async def determine_emoji(self, type):
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

