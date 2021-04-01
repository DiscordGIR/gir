import discord
from discord.ext import commands
import traceback
import asyncio
import re


class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cached_messages = {}

    @commands.command(name='setreactions', hidden=True)
    @commands.guild_only()
    @commands.max_concurrency(1, per=commands.BucketType.member, wait=False)
    async def setreactions(self, ctx: commands.Context, message_id: int):
        """Prompt to add multiple reaction roles to a message (admin only)

        Example usage
        -------------
        !setreactions <message ID>

        Parameters
        ----------
        message_id : int
            ID of message to add reactions to
        """

        if not ctx.guild.id == self.bot.settings.guild_id:
            return
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 6):
            raise commands.BadArgument(
                "You do not have permission to use this command.")
        channel = ctx.guild.get_channel(self.bot.settings.guild().channel_reaction_roles)

        if channel is None:
            return

        message = None
        try:
            message = await channel.fetch_message(message_id)
        except Exception:
            raise commands.BadArgument("Message not found.")

        def check_msg(m):
            return m.author == ctx.author and m.channel == ctx.channel

        reaction_mapping = {message.id: {}}
        stack = [ctx.message]
        reactions = []

        async def delete_stack(the_stack):
            for m in the_stack:
                try:
                    await m.delete()
                except Exception:
                    pass
            return []

        while True:
            prompt_embed = await ctx.send("Add the reaction to this message that you want to watch for (or :white_check_mark: to stop).")
            stack.append(prompt_embed)

            def check_reaction(reaction, user):
                return user.id == ctx.author.id and reaction.message.id == prompt_embed.id

            try:
                reaction, _ = await self.bot.wait_for('reaction_add', timeout=30.0, check=check_reaction)
            except asyncio.TimeoutError:
                try:
                    stack = await delete_stack(stack)
                    return
                except Exception:
                    pass
            else:
                if str(reaction.emoji) == "✅":
                    stack = await delete_stack(stack)
                    break

                if isinstance(reaction.emoji, discord.PartialEmoji) or (isinstance(reaction.emoji, discord.Emoji) and not reaction.emoji.available):
                    stack = await delete_stack(stack)
                    await ctx.send("That emoji is not available to me :(", delete_after=5)
                    continue

                while True:
                    stack = await delete_stack(stack)
                    try:
                        prompt_role = await ctx.send("Please enter a role ID to use for this react (or 'cancel' to stop)")
                        stack.append(prompt_role)
                        role_id = await self.bot.wait_for('message', check=check_msg, timeout=30.0)
                        stack.append(role_id)
                    except asyncio.TimeoutError:
                        stack = await delete_stack(stack)
                        return
                    else:
                        if role_id.content.lower() == 'cancel':
                            stack = await delete_stack(stack)
                            return
                        the_role = ctx.guild.get_role(int(role_id.content))
                        if the_role is None:
                            stack = await delete_stack(stack)
                        else:
                            reaction_mapping[message.id][str(reaction.emoji)] = the_role.id
                            reactions.append(reaction)
                            stack = await delete_stack(stack)
                            break

        await self.bot.settings.add_rero_mapping(reaction_mapping)
        the_string = "Done! We added the following emotes:\n"
        await message.clear_reactions()

        async with ctx.channel.typing():
            for r in reactions:
                the_string += f"Reaction {str(r)} will give role <@&{reaction_mapping[message.id][str(r.emoji)]}>\n"
                await message.add_reaction(r)

        await ctx.send(the_string, delete_after=10)

    @commands.command(name="newreaction")
    @commands.guild_only()
    @commands.max_concurrency(1, per=commands.BucketType.member, wait=False)
    async def newreaction(self, ctx, message_id: int):
        """Add one new reaction to a given message

        Example usage
        -------------
        !newreaction <message ID>

        Parameters
        ----------
        message : int
            Message to add reaction to
        """

        if not ctx.guild.id == self.bot.settings.guild_id:
            return
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 6):
            raise commands.BadArgument(
                "You do not have permission to use this command.")
        channel = ctx.guild.get_channel(self.bot.settings.guild().channel_reaction_roles)

        if channel is None:
            return

        rero_mapping = await self.bot.settings.get_rero_mapping(str(message_id))
        if rero_mapping is None:
            raise commands.BadArgument(f"Message with ID {message_id} had no reactions set in database. Use `!setreactions` first.")

        message = None
        try:
            message = await channel.fetch_message(message_id)
        except Exception:
            raise commands.BadArgument("Message not found.")

        def check_msg(m):
            return m.author == ctx.author and m.channel == ctx.channel

        reaction_mapping = {message.id: {}}
        stack = [ctx.message]
        reactions = []

        async def delete_stack(the_stack):
            for m in the_stack:
                try:
                    await m.delete()
                except Exception:
                    pass
            return []

        while True:
            prompt_embed = await ctx.send("Add the reaction to this message that you want to watch for (or :white_check_mark: to cancel).")
            stack.append(prompt_embed)

            def check_reaction(reaction, user):
                return user.id == ctx.author.id and reaction.message.id == prompt_embed.id

            try:
                reaction, _ = await self.bot.wait_for('reaction_add', timeout=30.0, check=check_reaction)
            except asyncio.TimeoutError:
                try:
                    stack = await delete_stack(stack)
                    return
                except Exception:
                    pass
            else:
                if str(reaction.emoji) == "✅":
                    stack = await delete_stack(stack)
                    return

                if isinstance(reaction.emoji, discord.PartialEmoji) or (isinstance(reaction.emoji, discord.Emoji) and not reaction.emoji.available):
                    stack = await delete_stack(stack)
                    await ctx.send("That emoji is not available to me :(", delete_after=5)
                    continue

                while True:
                    stack = await delete_stack(stack)
                    try:
                        prompt_role = await ctx.send("Please enter a role ID to use for this react (or 'cancel' to stop)")
                        stack.append(prompt_role)
                        role_id = await self.bot.wait_for('message', check=check_msg, timeout=30.0)
                        stack.append(role_id)
                    except asyncio.TimeoutError:
                        stack = await delete_stack(stack)
                        return
                    else:
                        if role_id.content.lower() == 'cancel':
                            stack = await delete_stack(stack)
                            return
                        the_role = ctx.guild.get_role(int(role_id.content))
                        if the_role is None:
                            stack = await delete_stack(stack)
                        else:
                            reaction_mapping[message.id][str(reaction.emoji)] = the_role.id
                            reactions.append(reaction)
                            stack = await delete_stack(stack)
                            break
                break

        await self.bot.settings.append_rero_mapping(reaction_mapping)
        the_string = "Done! We added the following emotes:\n"

        async with ctx.channel.typing():
            for r in reactions:
                the_string += f"Reaction {str(r)} will give role <@&{reaction_mapping[message.id][str(r.emoji)]}>\n"
                await message.add_reaction(r)

        await ctx.send(the_string, delete_after=10)

    @commands.command(name="movereactions")
    @commands.max_concurrency(1, per=commands.BucketType.member, wait=False)
    @commands.guild_only()
    async def movereactions(self, ctx, before: int, after: int):
        """Move reactions from one message to another.

        Example use
        -----------
        !movereactions <before message ID> <after message ID>

        Parameters
        ----------
        before : int
            ID of before messsage
        after : int
            ID of after message
        """

        if not ctx.guild.id == self.bot.settings.guild_id:
            return
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 6):
            raise commands.BadArgument(
                "You do not have permission to use this command.")

        if before == after:
            raise commands.BadArgument("I can't move to the same message.")

        channel = ctx.guild.get_channel(self.bot.settings.guild().channel_reaction_roles)

        if channel is None:
            return

        rero_mapping = await self.bot.settings.get_rero_mapping(str(before))
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

        await ctx.message.delete()
        rero_mapping = {after: rero_mapping}

        await self.bot.settings.add_rero_mapping(rero_mapping)
        await self.bot.settings.delete_rero_mapping(before)

        await after_message.clear_reactions()

        the_string = "Done! We added the following emotes:\n"
        async with ctx.channel.typing():
            for r in rero_mapping[after]:
                the_string += f"Reaction {str(r)} will give role <@&{rero_mapping[after][r]}>\n"
                await after_message.add_reaction(r)

        await ctx.send(the_string, delete_after=10)

    @commands.command(name="repostreactions")
    @commands.guild_only()
    async def repostreactions(self, ctx):
        """Repost all reactions to messages with reaction roles (admin only)
        """

        if not ctx.guild.id == self.bot.settings.guild_id:
            return
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 6):
            raise commands.BadArgument(
                "You do not have permission to use this command.")

        channel = ctx.guild.get_channel(self.bot.settings.guild().channel_reaction_roles)

        if channel is None:
            return

        rero_mapping = await self.bot.settings.all_rero_mappings()
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

        channel = payload.member.guild.get_channel(payload.channel_id)
        if payload.message_id not in self.cached_messages:
            message = await channel.fetch_message(payload.message_id)
            self.cached_messages[payload.message_id] = message
        else:
            message = self.cached_messages[payload.message_id]

        mapping = await self.bot.settings.get_rero_mapping(str(payload.message_id))
        if mapping is None:
            await message.remove_reaction(payload.emoji, payload.member)
            return

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
    @commands.guild_only()
    async def postembeds(self, ctx):
        """Post the reaction role embeds (admin only)
        """

        if not ctx.guild.id == self.bot.settings.guild_id:
            return
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 6):
            raise commands.BadArgument(
                "You do not have permission to use this command.")

        channel = ctx.guild.get_channel(self.bot.settings.guild().channel_reaction_roles)

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
    async def info_error(self, ctx, error):
        await ctx.message.delete(delay=5)
        if (isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.BotMissingPermissions)
            or isinstance(error, commands.MissingPermissions)
            or isinstance(error, commands.MaxConcurrencyReached)
                or isinstance(error, commands.NoPrivateMessage)):
            await self.bot.send_error(ctx, error)
        else:
            await self.bot.send_error(ctx, error)
            traceback.print_exc()


def setup(bot):
    bot.add_cog(ReactionRoles(bot))
