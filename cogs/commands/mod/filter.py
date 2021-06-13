import traceback

import discord
import cogs.utils.permission_checks as permissions
import cogs.utils.context as context
from data.filterword import FilterWord
from discord.ext import commands
from discord.ext import menus


class FilterSource(menus.GroupByPageSource):
    async def format_page(self, menu, entry):
        permissions = menu.ctx.bot.settings.permissions
        embed = discord.Embed(
            title=f'Filtered words', color=discord.Color.blurple())
        for _, word in entry.items:
            notify_flag = ""
            piracy_flag = ""
            flags_check = ""
            if word.notify is True:
                notify_flag = "🔔"
            if word.piracy:
                piracy_flag = " 🏴‍☠️"
            if word.notify is False and not word.piracy:
                flags_check = "None"
            embed.add_field(name=word.word, value=f"Bypassed by: {permissions.level_info(word.bypass)}\nFlags: {flags_check}{notify_flag}{piracy_flag}")
        embed.set_footer(
            text=f"Page {menu.current_page +1} of {self.get_max_pages()}")
        return embed


class MenuPages(menus.MenuPages):
    async def update(self, payload):
        if self._can_remove_reactions:
            if payload.event_type == 'REACTION_ADD':
                await self.message.remove_reaction(payload.emoji, payload.member)
            elif payload.event_type == 'REACTION_REMOVE':
                return
        await super().update(payload)


class Filters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.guild_only()
    @permissions.mod_and_up()
    @commands.command(name="offlineping")
    async def offlineping(self, ctx: context.Context, val: bool):
        """Bot will ping for reports when offline (mod only)

        Example usage:
        --------------
        `!offlineping <true/false>`

        Parameters
        ----------
        val : bool
            True or False, if you want pings or not

        """

        cur = await ctx.settings.user(ctx.author.id)
        cur.offline_report_ping = val
        cur.save()

        if val:
            await ctx.send_success("You will now be pinged for reports when offline")
        else:
            await ctx.send_warning("You will no longer be pinged for reports when offline")

    @commands.guild_only()
    @permissions.admin_and_up()
    @commands.command(name="filter")
    async def filteradd(self, ctx: context.Context, notify: bool, bypass: int, *, phrase: str) -> None:
        """Add a word to filter (admin only)

        Example usage:
        -------------
        `!filter false 5 :kek:`

        Parameters
        ----------
        notify : bool
            Whether to generate a report or not when this word is filtered
        bypass : int
            Level that can bypass this word
        phrase : str
            Phrase to filter
        """

        fw = FilterWord()
        fw.bypass = bypass
        fw.notify = notify
        fw.word = phrase

        await ctx.settings.add_filtered_word(fw)

        phrase = discord.utils.escape_markdown(phrase)
        phrase = discord.utils.escape_mentions(phrase)

        await ctx.send_success(title="Added new word to filter!", description=f"This filter {'will' if notify else 'will not'} ping for reports, level {bypass} can bypass it, and the phrase is `{phrase}`")

    @commands.guild_only()
    @permissions.admin_and_up()
    @commands.command(name="filterlist")
    async def filterlist(self, ctx: context.Context):
        """List filtered words (admin only)

        """

        filters = ctx.settings.guild().filter_words
        if len(filters) == 0:
            raise commands.BadArgument("The filterlist is currently empty. Please add a word using `!filter`.")
        
        filters = sorted(filters, key=lambda word: word.word.lower())

        menus = MenuPages(source=FilterSource(
            enumerate(filters), key=lambda t: 1, per_page=12), clear_reactions_after=True)

        await menus.start(ctx)

    @commands.guild_only()
    @permissions.admin_and_up()
    @commands.command(name="piracy")
    async def piracy(self, ctx: context.Context, *, word: str):
        """Mark a word as piracy, will be ignored in #dev (admin only)

        Example usage:
        --------------
        `!piracy xd xd xd`

        Parameters
        ----------
        word : str
            Word to mark as piracy

        """

        word = word.lower()

        words = ctx.settings.guild().filter_words
        words = list(filter(lambda w: w.word.lower() == word.lower(), words))
        
        if len(words) > 0:
            words[0].piracy = True
            await ctx.settings.update_filtered_word(words[0])

            await ctx.send_success("Marked as a piracy word!", delete_after=5)
        else:
            await ctx.send_warning("You must filter that word before it can be marked as piracy.", delete_after=5)            
        await ctx.message.delete(delay=5)

    @commands.guild_only()
    @permissions.admin_and_up()
    @commands.command(name="filterremove")
    async def filterremove(self, ctx: context.Context, *, word: str):
        """Remove word from filter (admin only)

        Example usage:
        --------------
        `!filterremove xd xd xd`

        Parameters
        ----------
        word : str
            Word to remove

        """

        word = word.lower()

        words = ctx.settings.guild().filter_words
        words = list(filter(lambda w: w.word.lower() == word.lower(), words))
        
        if len(words) > 0:
            await ctx.settings.remove_filtered_word(words[0].word)
            await ctx.send_success("Deleted!", delete_after=5)
        else:
            await ctx.send_warning("That word is not filtered.", delete_after=5)            
        await ctx.message.delete(delay=5)

    @commands.guild_only()
    @permissions.admin_and_up()
    @commands.command(name="whitelist")
    async def whitelist(self, ctx: context.Context, id: int):
        """Whitelist a guild from invite filter (admin only)

        Example usage:
        --------------
        `!whitelist 349243932447604736`

        Parameters
        ----------
        id : int
            ID of guild to whitelist

        """

        if await ctx.settings.add_whitelisted_guild(id):
            await ctx.send_success("Whitelisted.", delete_after=10)
        else:
            await ctx.send_warning("That server is already whitelisted.", delete_after=10)
        await ctx.message.delete(delay=10)

    @commands.guild_only()
    @permissions.admin_and_up()
    @commands.command(name="ignorechannel")
    async def ignorechannel(self, ctx: context.Context, channel: discord.TextChannel) -> None:
        """Ignore channel in filter (admin only)

        Example usage:
        -------------
        `!ignorechannel #xd`

        Parameters
        ----------
        channel : discord.Channel
            Channel to ignore

        """

        if await ctx.settings.add_ignored_channel(channel.id):
            await ctx.send_success(f"The filter will no longer run in {channel.mention}.", delete_after=10)
        else:
            await ctx.send_warning("That channel is already ignored.", delete_after=10)
        await ctx.message.delete(delay=10)

    @commands.guild_only()
    @permissions.admin_and_up()
    @commands.command(name="unignorechannel")
    async def unignorechannel(self, ctx: context.Context, channel: discord.TextChannel) -> None:
        """Unignore channel in filter (admin only)

        Example usage:
        -------------
        `!unignorechannel #xd`

        Parameters
        ----------
        channel : discord.Channel
            Channel to unignore
        """

        if await ctx.settings.remove_ignored_channel(channel.id):
            await ctx.send_success(f"Resumed filtering in {channel.mention}.", delete_after=10)
        else:
            await ctx.send_warning("That channel is not already ignored.", delete_after=10)
        await ctx.message.delete(delay=10)


    @commands.guild_only()
    @permissions.admin_and_up()
    @commands.command(name="blacklist")
    async def blacklist(self, ctx: context.Context, id: int):
        """Blacklist a guild from invite filter (admin only)

        Example usage:
        --------------
        `!blacklist 349243932447604736`

        Parameters
        ----------
        id : int
            ID of guild to blacklist

        """

        if await ctx.settings.remove_whitelisted_guild(id):
            await ctx.send_success("Blacklisted.", delete_after=10)
        else:
            await ctx.send_warning("That server is already blacklisted.", delete_after=10)
        await ctx.message.delete(delay=10)

    @commands.guild_only()
    @permissions.admin_and_up()
    @commands.command(name="falsepositive")
    async def falsepositive(self, ctx: context.Context, *, word: str):
        """Disabling enhanced filter checks on a word (admin only)

        Example usage:
        --------------
        `!falsepositive xd`

        Parameters
        ----------
        word : str
            Word to mark as false positive

        """

        word = word.lower()

        words = ctx.settings.guild().filter_words
        words = list(filter(lambda w: w.word.lower() == word.lower(), words))
        
        if len(words) > 0:
            words[0].false_positive=True
            if await ctx.settings.update_filtered_word(words[0]):
                await ctx.send_success("Marked as potential false positive, we won't perform the enhanced checks on it!")
            else:
                raise commands.BadArgument("Unexpected error occured trying to mark as false positive!")
        else:
            await ctx.send_warning("That word is not filtered.")  
            
    @falsepositive.error
    @piracy.error
    @whitelist.error
    @blacklist.error
    @filterremove.error
    @filteradd.error
    @filterlist.error
    @offlineping.error
    @ignorechannel.error
    @unignorechannel.error
    async def info_error(self, ctx: context.Context,error):
        await ctx.message.delete(delay=5)
        if (isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, permissions.PermissionsFailure)
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.MissingPermissions)
                or isinstance(error, commands.NoPrivateMessage)):
            await ctx.send_error(error)
        else:
            await ctx.send_error("A fatal error occured. Tell <@109705860275539968> about this.")
            traceback.print_exc()


def setup(bot):
    bot.add_cog(Filters(bot))
