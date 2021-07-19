import re
import traceback

import cogs.utils.context as context
import cogs.utils.permission_checks as permissions
import discord
from discord.ext import commands


class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cached_messages = {}

    @commands.command(name='setreactions', hidden=True)
    @commands.guild_only()
    @permissions.admin_and_up()
    @commands.max_concurrency(1, per=commands.BucketType.member, wait=False)
    async def setreactions(self, ctx: context.Context, message_id: int):
        """Prompt to add multiple reaction roles to a message (admin only)

        Example usage
        -------------
        !setreactions <message ID>

        Parameters
        ----------
        message_id : int
            "ID of message to add reactions to"
        """

        if not ctx.guild.id == ctx.settings.guild_id:
            return

        request_role_channel = ctx.guild.get_channel(ctx.settings.guild().channel_reaction_roles)

        if request_role_channel is None:
            return

        message = None
        try:
            message = await request_role_channel.fetch_message(message_id)
        except Exception:
            raise commands.BadArgument("Message not found.")

        reaction_mapping = {message.id: {}}
        
        while True:
            reaction = await self.prompt_for_reaction(ctx, reaction_mapping[message.id])
            
            if reaction is None:
                await ctx.send_warning("Timed out waiting for reaction, cancelling.", delete_after=5)
                await ctx.message.delete(delay=5)
                return
            elif str(reaction.emoji) == "✅":
                break
            elif isinstance(reaction.emoji, discord.PartialEmoji) or (isinstance(reaction.emoji, discord.Emoji) and not reaction.emoji.available):
                await ctx.send(embed=discord.Embed(description="That emoji is not available to me :(", color=discord.Color.dark_orange()), delete_after=5)
                continue
            
            role = await self.prompt_for_role(ctx, reaction, reaction_mapping[message.id])
            if role is None:
                await ctx.send_warning("Cancelled setting reactions.", delete_after=5)
                await ctx.message.delete(delay=5)
                return
            
            reaction_mapping[message.id][str(reaction.emoji)] = role.id

        if not reaction_mapping[message.id].keys():
            raise commands.BadArgument("Nothing to do.")

        await ctx.settings.add_rero_mapping(reaction_mapping)
        await message.clear_reactions()

        resulting_reactions_list = ""
        async with ctx.channel.typing():
            for r in reaction_mapping[message.id]:
                resulting_reactions_list += f"Reaction {r} will give role <@&{reaction_mapping[message.id][r]}>\n"
                await message.add_reaction(r)

        await ctx.send_success(title="Reaction roles set!", description=resulting_reactions_list, delete_after=10)
        await ctx.message.delete(delay=10)

    @commands.command(name="newreaction")
    @commands.guild_only()
    @permissions.admin_and_up()
    @commands.max_concurrency(1, per=commands.BucketType.member, wait=False)
    async def newreaction(self, ctx: context.Context, message_id: int):
        """Add one new reaction to a given message

        Example usage
        -------------
        !newreaction <message ID>

        Parameters
        ----------
        message : int
            "Message to add reaction to"
        """

        if not ctx.guild.id == ctx.settings.guild_id:
            return

        channel = ctx.guild.get_channel(ctx.settings.guild().channel_reaction_roles)

        if channel is None:
            return

        reaction_mapping = dict(await ctx.settings.get_rero_mapping(str(message_id)))
        if reaction_mapping is None:
            raise commands.BadArgument(f"Message with ID {message_id} had no reactions set in database. Use `!setreactions` first.")

        message = None
        try:
            message = await channel.fetch_message(message_id)
        except Exception:
            raise commands.BadArgument("Message not found.")
        
        while True:
            reaction = await self.prompt_for_reaction(ctx, reaction_mapping)
            
            if reaction is None:
                await ctx.send_warning("Timed out waiting for reaction, cancelling.", delete_after=5)
                await ctx.message.delete(delay=5)
                return
            elif str(reaction.emoji) in reaction_mapping:
                await ctx.message.delete(delay=5)
                raise commands.BadArgument(f"Reaction {str(reaction)} is already in use on that message.")
            elif str(reaction.emoji) == "✅":
                await ctx.send_warning("Cancelled adding new reaction.", delete_after=5)
                await ctx.message.delete(delay=5)
                return
            elif isinstance(reaction.emoji, discord.PartialEmoji) or (isinstance(reaction.emoji, discord.Emoji) and not reaction.emoji.available):
                await ctx.send(embed=discord.Embed(description="That emoji is not available to me :(", color=discord.Color.dark_orange()), delete_after=5)
                continue
            
            role = await self.prompt_for_role(ctx, reaction, reaction_mapping)
            if role is None:
                await ctx.send_warning("Cancelled setting reactions.", delete_after=5)
                await ctx.message.delete(delay=5)
                return
            elif role.id in reaction_mapping.values():
                await ctx.message.delete(delay=5)
                raise commands.BadArgument(f"There is already a reaction for {role.mention} on that message.")
            
            reaction_mapping[str(reaction.emoji)] = role.id
            break

        await ctx.settings.append_rero_mapping(message_id, reaction_mapping)
        await message.clear_reactions()

        resulting_reactions_list = ""
        async with ctx.channel.typing():
            for r in reaction_mapping:
                resulting_reactions_list += f"Reaction {r} will give role <@&{reaction_mapping[r]}>\n"
                await message.add_reaction(r)

        await ctx.send_success(title="Added new reaction!", description=resulting_reactions_list, delete_after=10)
        await ctx.message.delete(delay=10)

    async def prompt_for_reaction(self, ctx, reactions):
        text = "Please add the reaction to this message that you want to watch for (or :white_check_mark: to finish or cancel if nothing set so far)"
        if reactions:
            text += "\n\n**Current reactions**"
            for r in reactions:
                text += f"\n{r} <@&{reactions[r]}>"

        prompt_reaction_message = await ctx.send_success(description=text, title="Reaction roles")
        prompt_reaction = context.PromptDataReaction(
            message=prompt_reaction_message, 
            reactions=[], 
            timeout=30, 
            delete_after=True,
            raw_emoji=True)
        
        reaction, _ = await ctx.prompt_reaction(prompt_reaction)
        return reaction
    
    async def prompt_for_role(self, ctx, current_reaction, reactions):
        text = f"Please enter a role ID to use for {current_reaction} (or 'cancel' to stop)"
        if reactions:
            text += "\n\n**Current reactions**"
            for r in reactions:
                text += f"\n{r} <@&{reactions[r]}>"

        prompt_role = context.PromptData(value_name="role to give", 
                                            description=text, 
                                            convertor=commands.converter.RoleConverter().convert)
        
        return await ctx.prompt(prompt_role)

    @commands.command(name="movereactions")
    @commands.max_concurrency(1, per=commands.BucketType.member, wait=False)
    @permissions.admin_and_up()
    @commands.guild_only()
    async def movereactions(self, ctx: context.Context, before: int, after: int):
        """Move reactions from one message to another.

        Example use
        -----------
        !movereactions <before message ID> <after message ID>

        Parameters
        ----------
        before : int
            "ID of before messsage"
        after : int
            "ID of after message"
        """

        if not ctx.guild.id == ctx.settings.guild_id:
            return

        if before == after:
            raise commands.BadArgument("I can't move to the same message.")

        channel = ctx.guild.get_channel(ctx.settings.guild().channel_reaction_roles)

        if channel is None:
            return

        rero_mapping = await ctx.settings.get_rero_mapping(str(before))
        if rero_mapping is None:
            raise commands.BadArgument(f"Message with ID {before} had no reactions set in database.")

        try:
            after_message = await channel.fetch_message(after)
        except Exception:
            raise commands.BadArgument(f"Message with ID {after} not found.")

        try:
            before_message = await channel.fetch_message(before)
            await before_message.clear_reactions()
        except Exception:
            pass

        rero_mapping = {after: rero_mapping}

        await ctx.settings.add_rero_mapping(rero_mapping)
        await ctx.settings.delete_rero_mapping(before)

        await after_message.clear_reactions()

        resulting_reactions_list = "Done! We added the following emotes:\n"
        async with ctx.channel.typing():
            for r in rero_mapping[after]:
                resulting_reactions_list += f"Reaction {str(r)} will give role <@&{rero_mapping[after][r]}>\n"
                await after_message.add_reaction(r)

        await ctx.send_success(title="Reaction roles moved!", description=resulting_reactions_list, delete_after=10)
        await ctx.message.delete(delay=10)

    @commands.command(name="repostreactions")
    @permissions.admin_and_up()
    @commands.guild_only()
    async def repostreactions(self, ctx: context.Context):
        """Repost all reactions to messages with reaction roles (admin only)
        """

        if not ctx.guild.id == ctx.settings.guild_id:
            return

        channel = ctx.guild.get_channel(ctx.settings.guild().channel_reaction_roles)

        if channel is None:
            return

        rero_mapping = await ctx.settings.all_rero_mappings()
        if rero_mapping is None or rero_mapping == {}:
            raise commands.BadArgument("Nothing to do.")

        async with ctx.channel.typing():
            for m in rero_mapping:
                try:
                    message = await channel.fetch_message(int(m))
                except Exception:
                    continue
                await message.clear_reactions()
                for r in rero_mapping[m]:
                    await message.add_reaction(r)

        await ctx.message.delete()
        await ctx.send("Done!", delete_after=5)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return
        if not payload.guild_id:
            return
        if payload.channel_id != self.bot.settings.guild().channel_reaction_roles:
            return
        
        mapping = await self.bot.settings.get_rero_mapping(str(payload.message_id))
        if mapping is None:
            return

        channel = payload.member.guild.get_channel(payload.channel_id)
        if payload.message_id not in self.cached_messages:
            message = await channel.fetch_message(payload.message_id)
            self.cached_messages[payload.message_id] = message
        else:
            message = self.cached_messages[payload.message_id]

        if str(payload.emoji) not in mapping:
            await message.remove_reaction(payload.emoji, payload.member)
            return

        role = payload.member.guild.get_role(mapping[str(payload.emoji)])
        if role is None:
            await message.remove_reaction(payload.emoji)
            return

        try:
            if role not in payload.member.roles:
                await payload.member.add_roles(role)
            else:
                await payload.member.remove_roles(role)
        except Exception:
            pass

        await message.remove_reaction(payload.emoji, payload.member)

    @commands.command(name="postembeds")
    @permissions.admin_and_up()
    @commands.guild_only()
    @permissions.admin_and_up()
    async def postembeds(self, ctx):
        """Post the reaction role embeds (admin only)
        """

        if not ctx.guild.id == ctx.settings.guild_id:
            return

        channel = ctx.guild.get_channel(ctx.settings.guild().channel_reaction_roles)

        if channel is None:
            return

        def fix_emojis(desc):
            custom_emojis = re.findall(r':[^:\s]*(?:::[^:\s]*)*:', desc)
            for e in custom_emojis:
                old = e
                e = e.replace(':', '')
                replacement = discord.utils.get(self.bot.emojis, name=e)
                if replacement is not None:
                    desc = desc.replace(old, str(replacement))
            return desc

        embed = discord.Embed(title="Request a role")
        embed.color = discord.Color.purple()
        embed.set_author(name="Jailbreak Updates")
        embed.description = """
                            If you want to be notified about Checkra1n updates click :checkra1n:\nIf you want to be notified about Taurine updates click :taurine:\nIf you want to be notified about Unc0ver updates click :unc0ver:\nIf you want to be notified about tvOS Jailbreaks updates click :tvOSJailbreak:
                            """
        embed.description = fix_emojis(embed.description)
        await channel.send(embed=embed)

        embed = discord.Embed(title="Request a role")
        embed.color = discord.Color.red()
        embed.set_author(name="Software Updates")
        embed.description = """
                            If you want to be notified about iOS updates click :iOS:\nIf you want to be notified about iPadOS updates click :ipadOS:\nIf you want to be notified about tvOS updates click :tvOS:\nIf you want to be notified about macOS updates click :macOS:\nIf you want to be notified about watchOS updates click :watchOS:\nIf you want to be notified about any Other Apple Updates click :otherupdates:
                            """
        embed.description = fix_emojis(embed.description)
        await channel.send(embed=embed)

        embed = discord.Embed(title="Request a role")
        embed.color = discord.Color.green()
        embed.set_author(name="Other Updates")
        embed.description = """
                            If you want to be notified about Apple Events click :AppleEventNews:\nIf you want to be notified about Subreddit News click :SubredditNews:\nIf you want to be notified about any Community Events click :CommunityEvents:\nIf you want to be notified about any Giveaways click :giveaway:
                            """
        embed.description = fix_emojis(embed.description)
        await channel.send(embed=embed)

        await ctx.message.delete()
        await ctx.send("Done!", delete_after=5)

    @postembeds.error
    @newreaction.error
    @movereactions.error
    @setreactions.error
    async def info_error(self, ctx: context.Context, error):
        await ctx.message.delete(delay=5)
        if (isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, permissions.PermissionsFailure)
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.BotMissingPermissions)
            or isinstance(error, commands.MissingPermissions)
            or isinstance(error, commands.MaxConcurrencyReached)
                or isinstance(error, commands.NoPrivateMessage)):
            await ctx.send_error(error)
        else:
            await ctx.send_error(error)
            traceback.print_exc()


def setup(bot):
    bot.add_cog(ReactionRoles(bot))
