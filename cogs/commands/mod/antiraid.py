from discord.ext import commands
import discord
import traceback
import datetime

class AntiRaid(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.guild_only()
    @commands.command(name="raid")
    async def raid(self, ctx: commands.Context, *, phrase: str) -> None:
        """Add a phrase to the raid filter.

        Example Usage:
        --------------
        `!raid <phrase>`

        Parameters
        ----------
        phrase : str
            Phrase to add
        """

        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 6):
            raise commands.BadArgument("You need to be at least an Administrator to run that command.")
        
        done = await self.bot.settings.add_raid_phrase(phrase)
        if not done:
            raise commands.BadArgument("That phrase is already in the list.")
        else:
            one_week = datetime.date.today() + datetime.timedelta(days=7)
            self.bot.settings.tasks.schedule_remove_raid_phrase(phrase, one_week)
            await ctx.send(embed=discord.Embed(color=discord.Color.blurple(), description=f"Added {phrase} to the raid phrase list! This phrase will expire in one week."))
    
    @commands.guild_only()
    @commands.command(name="removeraid")
    async def removeraid(self, ctx: commands.Context, *, phrase: str) -> None:
        """Remove a phrase from the raid filter.

        Example Usage:
        --------------
        `!removeraid <phrase>`

        Parameters
        ----------
        phrase : str
            Phrase to remove
        """

        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 6):
            raise commands.BadArgument("You need to be at least an Administrator to run that command.")
        
        word = phrase.lower()

        words = self.bot.settings.guild().raid_phrases
        words = list(filter(lambda w: w.word.lower() == word.lower(), words))
        
        if len(words) > 0:
            await self.bot.settings.remove_raid_phrase(words[0].word)
            await ctx.message.reply(embed=discord.Embed(color=discord.Color.blurple(), description="Deleted!"))
        else:
            raise commands.BadArgument("That word is not a raid phrase.")            
    
    @removeraid.error
    @raid.error
    async def info_error(self, ctx, error):
        if (isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.BotMissingPermissions)
            or isinstance(error, commands.MissingPermissions)
                or isinstance(error, commands.NoPrivateMessage)):
            await self.bot.send_error(ctx, error)
        else:
            await self.bot.send_error(ctx, error)
            traceback.print_exc()

def setup(bot):
    bot.add_cog(AntiRaid(bot))