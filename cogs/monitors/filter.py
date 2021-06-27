import datetime
import re
import string

import cogs.utils.context as context
import cogs.utils.logs as logger
from cogs.utils.report import Report
import discord
import humanize
import pytimeparse
from data.case import Case
from discord.ext import commands
from fold_to_ascii import fold


class FilterCategories:
    def __init__(self):
        self.categories = {
            "default": FilterCategory(
                    name = "default",
                    color = None,
                    description = "asdf",
                    delete_after = True,
                    dm_only = True
                ),
            "piracy": FilterCategory(
                    name = "piracy",
                    color = None,
                    description = "asdf",
                    delete_after = True,
                    dm_only = True
                ),
        }
        
    def get(self, name: str):
        return self.categories.get(name)


class FilterMonitor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.filter_categories = FilterCategories()
        self.spoiler_filter = r'\|\|(.*?)\|\|'
        self.invite_filter = r'(?:https?://)?discord(?:(?:app)?\.com/invite|\.gg)\/{1,}[a-zA-Z0-9]+/?'
        self.spam_cooldown = commands.CooldownMapping.from_cooldown(2, 10.0, commands.BucketType.user)
        self.reports = Report(bot)

    async def do_filtering(self, message):
        if message.guild is not None and message.guild.id == self.bot.settings.guild_id:
            if not self.bot.settings.permissions.hasAtLeast(message.guild, message.author, 6):
                role_submod = message.guild.get_role(self.bot.settings.guild().role_sub_mod)
                if role_submod is not None:
                    if role_submod not in message.author.roles:
                        if await self.filter(message):
                            return True
                else:
                    if await self.filter(message):
                        return True
                                
        return False
    
    async def filter(self, message):
        if not message.guild:
            return False
        if message.author.bot:
            return False
        guild = self.bot.settings.guild()
        if message.guild.id != self.bot.settings.guild_id:
            return False
        if message.channel.id in guild.filter_excluded_channels:
            return False

        return await self.do_word_filter(message, guild) or await self.do_invite_filter(message) or await self.do_spoiler_filter(message, guild)
    
    async def do_word_filter(self, message, guild):
        """
        BAD WORD FILTER
        """
        symbols = (u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
                   u"abBrdeex3nnKnmHonpcTyoxu4wwbbbeoRABBrDEEX3NNKNMHONPCTyOXU4WWbbbEOR")

        tr = {ord(a): ord(b) for a, b in zip(*symbols)}

        folded_message = fold(message.content.translate(tr).lower()).lower()
        folded_without_spaces = "".join(folded_message.split())
        folded_without_spaces_and_punctuation = folded_without_spaces.translate(str.maketrans('', '', string.punctuation))
        word_found = False
        
        if folded_message:
            reported = False
            for word in guild.filter_words:
                if not self.bot.settings.permissions.hasAtLeast(message.guild, message.author, word.bypass):
                    if (word.word.lower() in folded_message) or \
                        (not word.false_positive and word.word.lower() in folded_without_spaces) or \
                        (not word.false_positive and word.word.lower() in folded_without_spaces_and_punctuation):
                        # remove all whitespace, punctuation in message and run filter again
                        if word.false_positive and word.word.lower() not in folded_message.split():
                            continue
                        
                        dev_role = message.guild.get_role(self.bot.settings.guild().role_dev)
                        # if not (word.piracy and message.channel.id == self.bot.settings.guild().channel_development and dev_role in message.author.roles):
                        if not (message.channel.id == self.bot.settings.guild().channel_development and dev_role in message.author.roles):
                            # ignore if this is a piracy word and the channel is #development and the user has dev role
                            word_found = True
                            await self.delete(message)
                            if not reported:
                                await self.do_filter_notify(message.author, message.channel, word.word)
                                await self.ratelimit(message)
                                reported = True
                            if word.notify:
                                await self.reports.report(message, message.author, word.word)
                                return True
        return word_found
    
    async def do_invite_filter(self, message):
        """
        INVITE FILTER
        """
        if message.content:
            if not self.bot.settings.permissions.hasAtLeast(message.guild, message.author, 5):
                invites = re.findall(self.invite_filter, message.content, flags=re.S)
                if invites:
                    whitelist = self.bot.settings.guild().filter_excluded_guilds
                    for invite in invites:
                        try:
                            invite = await self.bot.fetch_invite(invite)

                            id = None
                            if isinstance(invite, discord.Invite):
                                if invite.guild is not None:
                                    id = invite.guild.id
                                else:
                                    id = 123
                            elif isinstance(invite, discord.PartialInviteGuild) or isinstance(invite, discord.PartialInviteChannel):
                                id = invite.id

                            if id not in whitelist:
                                await self.delete(message)
                                await self.ratelimit(message)
                                await self.reports.report(message, message.author, invite, invite=invite)
                                return True

                        except discord.errors.NotFound:
                            await self.delete(message)
                            await self.ratelimit(message)
                            await self.reports.report(message, message.author, invite, invite=invite)
                            return True
        return False
    
    async def do_spoiler_filter(self, message, guild):
        """
        SPOILER FILTER
        """
        if not self.bot.settings.permissions.hasAtLeast(message.guild, message.author, 5):
            if re.search(self.spoiler_filter, message.content, flags=re.S):
                await self.delete(message)
                return True

            for a in message.attachments:
                if a.is_spoiler():
                    await self.delete(message)
                    return True

        """
        NEWLINE FILTER
        """
        if not self.bot.settings.permissions.hasAtLeast(message.guild, message.author, 5):
            if len(message.content.splitlines()) > 100:
                dev_role = message.guild.get_role(guild.role_dev)
                if not dev_role or dev_role not in message.author.roles:
                    await self.delete(message)
                    await self.ratelimit(message)
                    return True

        return False

    async def delete(self, message):
        try:
            await message.delete()
        except Exception:
            pass

    async def do_filter_notify(self, member, channel, word):
        message = f"Your message contained a word you aren't allowed to say in {member.guild.name}. This could be either hate speech or the name of a piracy tool/source. Please refrain from saying it!"
        footer = "Repeatedly triggering the filter will automatically result in a mute."
        try:
            embed = discord.Embed(description=f"{message}\n\nFiltered word found: **{word}**", color=discord.Color.orange())
            embed.set_footer(text=footer)
            await member.send(embed=embed)
        except Exception:
            embed = discord.Embed(description=message, color=discord.Color.orange())
            embed.set_footer(text=footer)
            await channel.send(member.mention, embed=embed, delete_after=10)

    async def mute(self, ctx: context.Context, user: discord.Member) -> None:
        dur = "15m"
        reason = "Filter spam"

        now = datetime.datetime.now()
        delta = pytimeparse.parse(dur)

        u = await self.bot.settings.user(id=user.id)
        mute_role = self.bot.settings.guild().role_mute
        mute_role = ctx.guild.get_role(mute_role)

        if mute_role in user.roles or u.is_muted:
            return

        case = Case(
            _id=self.bot.settings.guild().case_id,
            _type="MUTE",
            date=now,
            mod_id=ctx.me.id,
            mod_tag=str(ctx.me),
            reason=reason,
        )

        if delta:
            try:
                time = now + datetime.timedelta(seconds=delta)
                case.until = time
                case.punishment = humanize.naturaldelta(
                    time - now, minimum_unit="seconds")
                self.bot.settings.tasks.schedule_unmute(user.id, time)
            except Exception:
                raise commands.BadArgument(
                    "An error occured, this user is probably already muted")

        await self.bot.settings.inc_caseid()
        await self.bot.settings.add_case(user.id, case)
        u = await self.bot.settings.user(id=user.id)
        u.is_muted = True
        u.save()

        await user.add_roles(mute_role)

        log = await logger.prepare_mute_log(ctx.me, user, case)

        public_chan = ctx.guild.get_channel(self.bot.settings.guild().channel_public)
        if public_chan:
            log.remove_author()
            log.set_thumbnail(url=user.avatar_url)
            await public_chan.send(embed=log)

        try:
            await user.send(f"You have been muted in {ctx.guild.name}", embed=log)
        except Exception:
            pass           

    async def ratelimit(self, message):
        current = message.created_at.replace(tzinfo=datetime.timezone.utc).timestamp()

        bucket = self.spam_cooldown.get_bucket(message)
        if bucket.update_rate_limit(current):
            ctx = await self.get_context(message, cls=context.Context)
            await self.mute(ctx, message.author)
            
    @commands.Cog.listener()
    async def on_message_edit(self, _: discord.Message, after: discord.Message):
        await self.filter(after)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if not after.guild.id == self.bot.settings.guild_id:
            return
        if not before or not after:
            return
        if before.display_name == after.display_name:
            return
        if self.bot.settings.permissions.hasAtLeast(after.guild, after, 6):
            return

        await self.nick_filter(after)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Member) -> None:
        pending_task = self.reports.pending_tasks.get(message.id)
        if pending_task is not None:
            self.reports.pending_tasks[message.id] = "TERMINATE"
            

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        if member.guild.id != self.bot.settings.guild_id:
            return

        await self.nick_filter(member)

    async def nick_filter(self, member):
        if member.guild.id != self.bot.settings.guild_id:
            return

        guild = self.bot.settings.guild()
        nick = member.display_name

        symbols = (u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
                   u"abBrdeex3nnKnmHonpcTyoxu4wwbbbeoRABBrDEEX3NNKNMHONPCTyOXU4WWbbbEOR")

        tr = {ord(a): ord(b) for a, b in zip(*symbols)}

        folded_message = fold(nick.translate(tr).lower()).lower()
        folded_without_spaces = "".join(folded_message.split())
        folded_without_spaces_and_punctuation = folded_without_spaces.translate(str.maketrans('', '', string.punctuation))
        if folded_message:
            for word in guild.filter_words:
                if not self.bot.settings.permissions.hasAtLeast(member.guild, member, word.bypass):
                    if (word.word.lower() in folded_message) or \
                        (not word.false_positive and word.word.lower() in folded_without_spaces) or \
                        (not word.false_positive and word.word.lower() in folded_without_spaces_and_punctuation):
                        # remove all whitespace, punctuation in message and run filter again
                        if word.false_positive and word.word.lower() not in folded_message.split():
                            continue
                        await member.edit(nick="change name pls", reason=f"filter triggered ({nick})")
                        await self.do_filter_notify(member, word.word)
                        return
    
    async def do_filter_notify(self, member, word):
        message = f"Your nickname contained a word you aren't allowed to say in {member.guild.name}. This could be either hate speech or the name of a piracy tool/source. We've automatically changed your name."
        try:
            embed = discord.Embed(description=f"{message}\n\nFiltered word found: **{word}**", color=discord.Color.orange())
            await member.send(embed=embed)
        except Exception:
            pass


class FilterCategory:
    def __init__(self, name, color, description, delete_after, dm_only):
        self.name = name
        self.color = color
        self.description = description
        self.delete_after = delete_after
        self.dm_only = dm_only


def setup(bot):
    bot.add_cog(FilterMonitor(bot))
