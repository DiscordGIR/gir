import traceback

import discord
from data.filterword import FilterWord
from discord.ext import commands


class Filters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.guild_only()
    @commands.command(name="offlineping")
    async def offlineping(self, ctx, val: bool):
        """Bot will ping for reports when offline (mod only)

        Example usage:
        --------------
        `!offlineping <true/false>`

        Parameters
        ----------
        val : bool
            True or False, if you want pings or not

        """

        # must be at least a mod
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 5):
            raise commands.BadArgument(
                "You need to be a moderator or higher to use that command.")

        cur = await self.bot.settings.user(ctx.author.id)
        cur.offline_report_ping = val
        cur.save()

        if val:
            await ctx.send("You will now be pinged for reports when offline")
        else:
            await ctx.send("You won't be pinged for reports when offline")

    @commands.guild_only()
    @commands.command(name="filter")
    async def filteradd(self, ctx, notify: bool, bypass: int, *, phrase: str) -> None:
        """Add a word to filter (admin only)

        Example usage:
        -------------
        `!filteradd false 5 :kek:`

        Parameters
        ----------
        notify : bool
            Whether to generate a report or not when this word is filtered
        bypass : int
            Level that can bypass this word
        phrase : str
            Phrase to filter
        """

        # must be at least admin
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 6):
            await ctx.message.delete()
            raise commands.BadArgument(
                "You need to be an administator or higher to use that command.")

        fw = FilterWord()
        fw.bypass = bypass
        fw.notify = notify
        fw.word = phrase

        await self.bot.settings.add_filtered_word(fw)

        phrase = discord.utils.escape_markdown(phrase)
        phrase = discord.utils.escape_mentions(phrase)

        await ctx.message.reply(f"Added new word to filter! This filter {'will' if notify else 'will not'} ping for reports, level {bypass} can bypass it, and the phrase is {phrase}")

    @commands.guild_only()
    @commands.command(name="filterremove")
    async def filterremove(self, ctx, *, word:str):
        """Remove word from filter (admin only)

        Example usage:
        --------------
        `!filterremove xd xd xd`

        Parameters
        ----------
        word : str
            Word to remove

        """
        # must be at least admin
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 6):
            await ctx.message.delete()
            raise commands.BadArgument(
                "You need to be an administator or higher to use that command.")
        
        word = word.lower()
        await self.bot.settings.remove_filtered_word(word)
        await ctx.message.reply("Deleted, if it exists :p", delete_after=10)
    
    @commands.guild_only()
    @commands.command(name="whitelist")
    async def whitelist(self, ctx, id:int):
        """Whitelist a guild from invite filter (admin only)

        Example usage:
        --------------
        `!whitelist 349243932447604736`

        Parameters
        ----------
        id : int
            ID of guild to whitelist

        """

        # must be at least admin
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 6):
            await ctx.message.delete()
            raise commands.BadArgument(
                "You need to be an administator or higher to use that command.")
        
        await self.bot.settings.add_whitelisted_guild(id)
        await ctx.message.reply("Whitelisted.", delete_after=10)
        

    @whitelist.error
    @filterremove.error
    @filteradd.error
    @offlineping.error
    async def info_error(self, ctx, error):
        if (isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.MissingPermissions)
                or isinstance(error, commands.NoPrivateMessage)):
            await self.bot.send_error(ctx, error)
        else:
            await self.bot.send_error(ctx, "A fatal error occured. Tell <@109705860275539968> about this.")
            traceback.print_exc()


def setup(bot):
    bot.add_cog(Filters(bot))
