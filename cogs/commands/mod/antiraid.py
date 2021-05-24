from discord.ext import commands
import discord
import datetime

class AntiRaid(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.guild_only()
    @commands.command(name="raidphrase")
    async def raidphrase(self, ctx: commands.Context, phrase: str) -> None:
        """Add a phrase to the raid filter.

        Example Usage:
        --------------
        `!raidphrase <phrase>`

        Parameters
        ----------
        phrase : str
            Phrase to add
        """

        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 5):
            raise commands.BadArgument("You need to be at least a Moderator to run that command.")
        
        done = await self.bot.settings.add_raid_phrase(phrase)
        if not done:
            await ctx.send("That phrase is already in the list.")
        else:
            one_week = datetime.date.today() + datetime.timedelta(days=7)
            self.bot.settings.tasks.schedule_remove_raid_phrase(phrase, one_week)
            await ctx.send(f"Added {phrase} to the raid phrase list! This phrase will expire in one week.")
    
    @raidphrase.error
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