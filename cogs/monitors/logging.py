from datetime import datetime
from io import BytesIO

import discord
from discord.ext import commands


class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

        channel = discord.utils.get(
            member.guild.channels, id=self.bot.settings.guild().channel_private)

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
        embed.set_footer(text=member.id)
        await channel.send(embed=embed)

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

        channel = discord.utils.get(
            member.guild.channels, id=self.bot.settings.guild().channel_private)

        embed = discord.Embed(title="Member left")
        embed.color = discord.Color.purple()
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(
            name="User", value=f'{member} ({member.mention})', inline=True)
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
        if before.content == after.content:
            return

        channel = discord.utils.get(
            before.guild.channels, id=self.bot.settings.guild().channel_private)

        embed = discord.Embed(title="Message Updated")
        embed.color = discord.Color.purple()
        embed.set_thumbnail(url=before.author.avatar_url)
        embed.add_field(
            name="User", value=f'{before.author} ({before.author.mention})', inline=False)
        embed.add_field(name="Old message", value=before.content, inline=False)
        embed.add_field(name="New message", value=before.content, inline=False)
        embed.add_field(
            name="Channel", value=before.channel.mention, inline=False)
        embed.set_footer(text=before.author.id)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        """Log message deletes

        Parameters
        ----------
        message : discord.Message
            Message that was deleted
        """

        if not message.guild:
            return
        if message.guild.id != self.bot.settings.guild_id:
            return
        if message.author.bot:
            return
        if message.content == "" or not message.content:
            return

        channel = discord.utils.get(
            message.guild.channels, id=self.bot.settings.guild().channel_private)

        embed = discord.Embed(title="Message Deleted")
        embed.color = discord.Color.red()
        embed.set_thumbnail(url=message.author.avatar_url)
        embed.add_field(
            name="User", value=f'{message.author} ({message.author.mention})', inline=True)
        embed.add_field(
            name="Channel", value=message.channel.mention, inline=True)
        embed.add_field(name="Message", value=message.content, inline=False)
        embed.set_footer(text=message.author.id)
        embed.timestamp = datetime.now()
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages: [discord.Message]):
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
        channel = discord.utils.get(
            messages[0].guild.channels, id=self.bot.settings.guild().channel_private)
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
        await channel.send(embed=embed)
        await channel.send(file=discord.File(output, 'message.txt'))

    @commands.Cog.listener()
    async def on_message(self, message):
        """NSA: mirror all messages to NSA server

        Parameters
        ----------
        message : discord.Message
            Message to log
        """

        if message.guild:
            if message.guild.id != self.bot.settings.guild_id:
                return
        else:
            return

        # get NSA guild object
        nsa = self.bot.get_guild(id=self.bot.settings.guild().nsa_guild_id)
        # get channel ID of the mirror channel in NSA from db, webhook ID
        nsa_channel_info = await self.bot.settings.get_nsa_channel(message.channel.id)
        nsa_webhook = None

        # if we don't have a mirror channel in db, generate one and store in db
        if nsa_channel_info is None:
            nsa_channel = await self.gen_channel(nsa, message)
            nsa_webhook = await nsa_channel.create_webhook(name="NSA default")

            await self.bot.settings.add_nsa_channel(message.channel.id, nsa_channel.id, nsa_webhook.id)

        else:
            # get the NSA channel object from Discord
            nsa_channel = discord.utils.get(
                nsa.channels, id=nsa_channel_info["channel_id"])

            # channel no longer exists, make new one and store in db
            if not nsa_channel:
                nsa_channel = await self.gen_channel(nsa, message)
                nsa_webhook = await nsa_channel.create_webhook(name="NSA default")

                await self.bot.settings.add_nsa_channel(message.channel.id, nsa_channel.id, nsa_webhook.id)

            else:
                # try to get webhook instance, if doesn't exist, make new one and update db
                try:
                    nsa_webhook = await self.bot.fetch_webhook(nsa_channel_info["webhook_id"])
                except:
                    nsa_webhook = await nsa_channel.create_webhook(name="NSA default")
                    await self.bot.settings.add_nsa_channel(message.channel.id, nsa_channel.id, nsa_webhook.id)

        # send the log
        await nsa_webhook.send(
            content=f"**{message.author.id}** {message.content}",
            username=str(message.author),
            avatar_url=message.author.avatar_url,
            embeds=message.embeds,
            files=[await a.to_file() for a in message.attachments] or None,
            allowed_mentions=discord.AllowedMentions().none()
        )

    async def gen_channel(self, nsa, message):
        main_category_name = message.channel.category.name
        nsa_category = discord.utils.get(
            nsa.categories, name=main_category_name)
        if not nsa_category:
            nsa_category = await nsa.create_category(main_category_name, position=message.channel.category.position)

        return await nsa_category.create_text_channel(name=message.channel.name, position=message.channel.position)

    async def info_error(self, ctx, error):
        if (isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.MissingPermissions)
                or isinstance(error, commands.NoPrivateMessage)):
            await self.bot.send_error(ctx, error)
        else:
            traceback.print_exc()


def setup(bot):
    bot.add_cog(Logging(bot))
