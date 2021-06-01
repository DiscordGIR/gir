import traceback
from datetime import datetime
from io import BytesIO

import discord
from discord.ext import commands
from collections import defaultdict
import cogs.utils.context as context
from fold_to_ascii import fold
from typing import List

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.webhook_dict = defaultdict(lambda: False)
        self.emoji_webhook = defaultdict(lambda: False)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, member: discord.Member):
        if isinstance(member, discord.ClientUser) or member.guild is None:
            return
        if member.bot:
            return
        if member.guild.id != self.bot.settings.guild_id:
            return

        webhook_id = self.bot.settings.guild().emoji_logging_webhook
        webhook = None

        if webhook_id is not None:
            webhook = self.webhook_dict[webhook_id]
            if not webhook:
                try:
                    webhook = await self.bot.fetch_webhook(webhook_id)
                    self.webhook_dict[webhook_id] = webhook
                except Exception:
                    pass

        if webhook_id is None or webhook is None:
            channel = member.guild.get_channel(self.bot.settings.guild().channel_emoji_log)
            if channel:
                webhook = await channel.create_webhook(name="logging emojis")
                self.webhook_dict[webhook.id] = webhook_id
                await self.bot.settings.save_emoji_webhook(webhook.id)
            else:
                return

        embed = discord.Embed(title="Member added reaction")
        embed.color = discord.Color.green()
        embed.add_field(
            name="User", value=f'{member} ({member.mention})', inline=True)
        embed.add_field(
            name="Reaction", value=reaction.emoji, inline=True)
        embed.add_field(
            name="Message", value=f"[Link to message]({reaction.message.jump_url})\nby {reaction.message.author} ({reaction.message.author.id})", inline=False)
        embed.timestamp = datetime.now()
        embed.set_footer(text=member.id)

        try:
            await webhook.send(
                username=str(self.bot.user.name),
                avatar_url=self.bot.user.avatar_url,
                embed=embed
            )
        except Exception:
            pass

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        """Log member join messages, send log to #server-logs

        Parameters
        ----------
        member : discord.Member
            The member that joined
        """

        if member.guild.id != self.bot.settings.guild_id:
            return

        channel = member.guild.get_channel(self.bot.settings.guild().channel_private)

        embed = discord.Embed(title="Member joined")
        embed.color = discord.Color.green()
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(
            name="User", value=f'{member} ({member.mention})', inline=True)
        embed.add_field(name="Warnpoints", value=(await self.bot.settings.user(member.id)).warn_points, inline=True)
        embed.add_field(name="Joined", value=member.joined_at.strftime(
            "%B %d, %Y, %I:%M %p") + " UTC", inline=False)
        embed.add_field(name="Created", value=member.created_at.strftime(
            "%B %d, %Y, %I:%M %p") + " UTC", inline=True)
        embed.timestamp = datetime.now()
        embed.set_footer(text=member.id)

        await channel.send(embed=embed)

        u = await self.bot.settings.user(id=member.id)
        if u.is_muted:
            mute_role = self.bot.settings.guild().role_mute
            mute_role = member.guild.get_role(mute_role)
            await member.add_roles(mute_role)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        """Log member leaves in #server-logs

        Parameters
        ----------
        member : discord.Member
            Member that left
        """

        if member.guild.id != self.bot.settings.guild_id:
            return

        channel = member.guild.get_channel(self.bot.settings.guild().channel_private)

        embed = discord.Embed(title="Member left")
        embed.color = discord.Color.purple()
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(
            name="User", value=f'{member} ({member.mention})', inline=True)
        embed.timestamp = datetime.now()
        embed.set_footer(text=member.id)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        """Log message edits with before and after content

        Parameters
        ----------
        before : discord.Message
            Before edit message data
        after : discord.Message
            Aftere edit message data
        """

        if not before.guild:
            return
        if before.guild.id != self.bot.settings.guild_id:
            return
        if not before.content or not after.content or before.content == after.content:
            return

        channel = before.guild.get_channel(self.bot.settings.guild().channel_private)

        embed = discord.Embed(title="Message Updated")
        embed.color = discord.Color.orange()
        embed.set_thumbnail(url=before.author.avatar_url)
        embed.add_field(
            name="User", value=f'{before.author} ({before.author.mention})', inline=False)
        before_content = before.content
        if len(before.content) > 400:
            before_content = before_content[0:400] + "..."
        after_content = after.content
        if len(after.content) > 400:
            after_content = after_content[0:400] + "..."
        embed.add_field(name="Old message", value=before_content, inline=False)
        embed.add_field(name="New message", value=after_content, inline=False)
        embed.add_field(
            name="Channel", value=before.channel.mention + f"\n\n[Link to message]({before.jump_url})", inline=False)
        embed.timestamp = datetime.now()
        embed.set_footer(text=before.author.id)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent) -> None:
        """Log message deletes

        Parameters
        ----------
        message : discord.Message
            Message that was deleted
        """

        message = payload.cached_message

        if not message or not message.guild:
            return
        if message.guild.id != self.bot.settings.guild_id:
            return
        if message.author.bot:
            return
        if message.content == "" or not message.content:
            return

        channel = message.guild.get_channel(self.bot.settings.guild().channel_private)

        embed = discord.Embed(title="Message Deleted")
        embed.color = discord.Color.red()
        embed.set_thumbnail(url=message.author.avatar_url)
        embed.add_field(
            name="User", value=f'{message.author} ({message.author.mention})', inline=True)
        embed.add_field(
            name="Channel", value=message.channel.mention, inline=True)
        content = message.content
        if len(message.content) > 400:
            content = content[0:400] + "..."
        embed.add_field(name="Message", value=content + f"\n\n[Link to message]({message.jump_url})", inline=False)
        embed.set_footer(text=message.author.id)
        embed.timestamp = datetime.now()
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: context.Context, error):
        if isinstance(error, commands.CommandNotFound):
            return

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages: List[discord.Message]):
        """Log bulk message deletes. Messages are outputted to file and sent to #server-logs

        Parameters
        ----------
        messages : [discord.Message]
            List of messages that were deleted
        """

        if not messages[0].guild:
            return
        if messages[0].guild.id != self.bot.settings.guild_id:
            return

        members = set()
        channel = messages[0].guild.get_channel(self.bot.settings.guild().channel_private)
        output = BytesIO()
        for message in messages:
            members.add(message.author)

            string = f'{message.author} ({message.author.id}) [{message.created_at.strftime("%B %d, %Y, %I:%M %p")}]) UTC\n'
            string += message.content
            for attachment in message.attachments:
                string += f'\n{attachment.url}'

            string += "\n\n"
            output.write(string.encode('UTF-8'))
        output.seek(0)

        member_string = ""
        for i, member in enumerate(members):
            if i == len(members) - 1 and i == 0:
                member_string += f"{member.mention}"
            elif i == len(members) - 1 and i != 0:
                member_string += f"and {member.mention}"
            else:
                member_string += f"{member.mention}, "

        embed = discord.Embed(title="Bulk Message Deleted")
        embed.color = discord.Color.red()
        embed.add_field(
            name="Users", value=f'This batch included {len(messages)} messages from {member_string}', inline=True)
        embed.add_field(
            name="Channel", value=message.channel.mention, inline=True)
        embed.timestamp = datetime.now()
        await channel.send(embed=embed)
        await channel.send(file=discord.File(output, 'message.txt'))

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Message, after: discord.Message):
        if not after.guild.id == self.bot.settings.guild_id:
            return
        if not before or not after:
            return
        if before.display_name != after.display_name:
            await self.member_nick_update(before, after)
            return

        new_roles = [str(role) for role in after.roles if role not in before.roles]
        if new_roles:
            await self.member_roles_update(before, after, new_roles, added=True)
            return

        removed_roles = [str(role) for role in before.roles if role not in after.roles]
        if removed_roles:
            await self.member_roles_update(before, after, removed_roles, added=False)
            return

    async def member_nick_update(self, before, after):
        embed = discord.Embed(title="Member Renamed")
        embed.color = discord.Color.orange()
        embed.set_thumbnail(url=after.avatar_url)
        embed.add_field(
            name="Member", value=f'{after} ({after.mention})', inline=False)
        embed.add_field(
            name="Old nickname", value=f'{before.display_name}', inline=True)
        embed.add_field(
            name="New nickname", value=f'{after.display_name}', inline=True)
        embed.timestamp = datetime.now()
        embed.set_footer(text=after.id)

        private = after.guild.get_channel(self.bot.settings.guild().channel_private)
        if private:
            await private.send(embed=embed)

    async def member_roles_update(self, before, after, roles, added):
        embed = discord.Embed()
        if added:
            embed.title = "Member Role Added"
            embed.color = discord.Color.blue()
        else:
            embed.title = "Member Role Removed"
            embed.color = discord.Color.red()

        embed.set_thumbnail(url=after.avatar_url)
        embed.add_field(
            name="Member", value=f'{after} ({after.mention})', inline=False)
        embed.add_field(
            name="Role difference", value=', '.join(roles), inline=False)
        embed.timestamp = datetime.now()
        embed.set_footer(text=after.id)

        private = after.guild.get_channel(self.bot.settings.guild().channel_private)
        if private:
            await private.send(embed=embed)


def setup(bot):
    bot.add_cog(Logging(bot))
