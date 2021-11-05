import traceback
import typing

from discord.embeds import Embed

import cogs.utils.context as context
import cogs.utils.permission_checks as permissions
import discord
from discord.ext import commands


class AntiRaid(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.guild_only()
    @permissions.mod_and_up()
    @commands.command(name="raid", aliases=["raidphrase"])
    async def raid(self, ctx: context.Context, *, phrase: str) -> None:
        """Add a phrase to the raid filter.

        Example usage
        --------------
        !raid <phrase>

        Parameters
        ----------
        phrase : str
            "Phrase to add"
        """
        
        # these are phrases that when said by a whitename, automatically bans them.
        # for example: known scam URLs
        done = await ctx.settings.add_raid_phrase(phrase)
        if not done:
            raise commands.BadArgument("That phrase is already in the list.")
        else:
            await ctx.send_success(description=f"Added `{phrase}` to the raid phrase list!")
    
    @commands.guild_only()
    @permissions.admin_and_up()
    @commands.command(name="batchraid", aliases=["raidbatch"])
    async def batchraid(self, ctx: context.Context, *, phrases: str) -> None:
        """Add a list of (newline-separated) phrases to the raid filter.

        Example usage
        --------------
        !raid <phrase>

        Parameters
        ----------
        phrases : str
            "Phrases to add, separated with enter"
        """
        
        async with ctx.typing():
            phrases = list(set(phrases.split("\n")))
            phrases = [phrase.strip() for phrase in phrases]
            
            phrases_contenders = set(phrases)
            phrases_already_in_db = set([phrase.word for phrase in ctx.settings.guild().raid_phrases])
            
            duplicate_count = len(phrases_already_in_db & phrases_contenders) # count how many duplicates we have
            new_phrases = list(phrases_contenders - phrases_already_in_db)
            
        if not new_phrases:
            raise commands.BadArgument("All the phrases you supplied are already in the database.")
            
        phrases_prompt_string = "\n".join([f"**{i+1}**. {phrase}" for i, phrase in enumerate(new_phrases)])
        if len(phrases_prompt_string) > 3900:
            phrases_prompt_string = phrases_prompt_string[:3500] + "\n... (and some more)"

        embed = Embed(title="Confirm raidphrase batch", 
                    color=discord.Color.dark_orange(), 
                    description=f"{phrases_prompt_string}\n\nShould we add these {len(new_phrases)} phrases?")
        
        if duplicate_count > 0:
            embed.set_footer(text=f"Note: we found {duplicate_count} duplicates in your list.")
        
        message = await ctx.send(embed=embed)
            
        prompt_data = context.PromptDataReaction(message=message, reactions=['✅', '❌'], timeout=120, delete_after=True)
        response, _ = await ctx.prompt_reaction(info=prompt_data)
        
        if response == '✅':
            async with ctx.typing():
                for phrase in new_phrases:
                    await ctx.settings.add_raid_phrase(phrase)

            await ctx.send_success(f"Added {len(new_phrases)} phrases to the raid filter.", delete_after=5)
        else:
            await ctx.send_warning("Cancelled.", delete_after=5)

        await ctx.message.delete(delay=5)

    @commands.guild_only()
    @permissions.mod_and_up()
    @commands.command(name="removeraid", aliases=["removeraidphrase"])
    async def removeraid(self, ctx: context.Context, *, phrase: str) -> None:
        """Remove a phrase from the raid filter.

        Example usage
        --------------
        !removeraid <phrase>

        Parameters
        ----------
        phrase : str
            "Phrase to remove"
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

        Example usage
        --------------
        !spammode true
        """
        
        if mode is None:
            mode = not ctx.settings.guild().ban_today_spam_accounts
        
        await ctx.settings.set_spam_mode(mode)
        await ctx.send_success(description=f"We {'**will ban**' if mode else 'will **not ban**'} accounts created today in join spam filter.", delete_after=10)
        await ctx.message.delete(delay=5)

    @commands.guild_only()
    @permissions.admin_and_up()
    @commands.command(name="verify")
    async def verify(self, ctx: context.Context, user: permissions.ModsAndAboveExternal, mode: bool = None) -> None:
        """Verify a user so they won't be banned by antiraid filters.

        Example usage
        --------------
        !verify @user
        !verify @user true/false
        """
        
        profile = await ctx.settings.user(user.id)
        if mode is None:
            profile.raid_verified = not profile.raid_verified
        else:
            profile.raid_verified = mode
        
        profile.save()
        
        await ctx.settings.set_spam_mode(mode)
        await ctx.send_success(description=f"{'**Verified**' if profile.raid_verified else '**Unverified**'} user {user.mention}.", delete_after=5)
        await ctx.message.delete(delay=5)
    
    @verify.error
    @spammode.error
    @removeraid.error
    @batchraid.error
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
