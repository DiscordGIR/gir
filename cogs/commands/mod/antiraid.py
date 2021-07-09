from discord.ext import commands
import cogs.utils.permission_checks as permissions
import cogs.utils.context as context
import discord
import traceback
import datetime

class AntiRaid(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.guild_only()
    @permissions.admin_and_up()
    @commands.command(name="raid")
    async def raid(self, ctx: context.Context, *, phrase: str) -> None:
        """Add a phrase to the raid filter.

        Example Usage:
        --------------
        `!raid <phrase>`

        Parameters
        ----------
        phrase : str
            Phrase to add
        """
        
        done = await ctx.settings.add_raid_phrase(phrase)
        if not done:
            raise commands.BadArgument("That phrase is already in the list.")
        else:
            # one_week = datetime.date.today() + datetime.timedelta(days=7)
            # ctx.tasks.schedule_remove_raid_phrase(phrase, one_week)
            await ctx.send_success(description=f"Added `{phrase}` to the raid phrase list!")
    
    @commands.guild_only()
    @permissions.admin_and_up()
    @commands.command(name="removeraid")
    async def removeraid(self, ctx: context.Context, *, phrase: str) -> None:
        """Remove a phrase from the raid filter.

        Example Usage:
        --------------
        `!removeraid <phrase>`

        Parameters
        ----------
        phrase : str
            Phrase to remove
        """
        
        word = phrase.lower()

        words = ctx.settings.guild().raid_phrases
        words = list(filter(lambda w: w.word.lower() == word.lower(), words))
        
        if len(words) > 0:
            await ctx.settings.remove_raid_phrase(words[0].word)
            await ctx.send_success("Deleted!", delete_after=5)
        else:
            raise commands.BadArgument("That word is not a raid phrase.")            

    @commands.guild_only()
    @permissions.admin_and_up()
    @commands.command(name="spammode")
    async def spammode(self, ctx: context.Context, mode: bool = None) -> None:
        """Toggle banning of *today's* new accounts in join spam detector.

        Example Usage:
        --------------
        `!spammode true`

        Parameters
        ----------
        phrase : str
            Phrase to remove
        """
        
        if mode is None:
            mode = not ctx.settings.guild().ban_today_spam_accounts
        
        await ctx.settings.set_spam_mode(mode)
        await ctx.send_success(description=f"We {'**will ban**' if mode else 'will **not ban**'} accounts created today in join spam filter.", delete_after=10)
        await ctx.message.delete(delay=5)
    
    @spammode.error
    @removeraid.error
    @raid.error
    async def info_error(self, ctx: context.Context,error):
        await ctx.message.delete(delay=5)
        if (isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, permissions.PermissionsFailure)
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.BotMissingPermissions)
            or isinstance(error, commands.MissingPermissions)
                or isinstance(error, commands.NoPrivateMessage)):
            await ctx.send_error(error)
        else:
            await ctx.send_error(error)
            traceback.print_exc()

def setup(bot):
    bot.add_cog(AntiRaid(bot))