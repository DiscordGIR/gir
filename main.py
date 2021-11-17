import datetime
import logging
import re
import os
import string

import discord
import humanize
import pytimeparse
from data.case import Case
import cogs.utils.logs as logger
import cogs.utils.context as context
from discord.ext import commands
from dotenv import find_dotenv, load_dotenv
from fold_to_ascii import fold

from cogs.monitors.report import Report

logging.basicConfig(level=logging.INFO)

load_dotenv(find_dotenv())


def get_prefix(bot, message):
    """A callable Prefix for our bot. This could be edited to allow per server prefixes."""

    prefixes = ['!']

    # If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(bot, message)


initial_extensions = [
                    'cogs.commands.mod.modactions',
                    'cogs.commands.mod.modutils',
                    'cogs.commands.mod.antiraid',
                    'cogs.commands.mod.trivia',
                    'cogs.commands.misc.admin',
                    'cogs.commands.misc.genius',
                    'cogs.commands.misc.misc',
                    'cogs.commands.misc.subnews',
                    'cogs.commands.misc.giveaway',
                    'cogs.commands.misc.parcility',
                    'cogs.commands.info.devices',
                    'cogs.commands.info.help',
                    'cogs.commands.info.stats',
                    'cogs.commands.info.tags',
                    'cogs.commands.info.userinfo',
                    'cogs.commands.mod.filter',
                    'cogs.monitors.antiraid',
                    'cogs.monitors.applenews',
                    'cogs.monitors.birthday',
                    'cogs.monitors.boosteremojis',
                    'cogs.monitors.filter',
                    'cogs.monitors.logging',
                    'cogs.monitors.reactionroles',
                    'cogs.monitors.xp',
]

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.presences = True
mentions = discord.AllowedMentions(everyone=False, users=True, roles=False)

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_extension('cogs.utils.settings')
        self.settings = self.get_cog("Settings")
        self.spoiler_filter = r'\|\|(.*?)\|\|'
        self.invite_filter = r'(?:https?://)?discord(?:(?:app)?\.com/invite|\.gg)\/{1,}[a-zA-Z0-9]+/?'
        self.spam_cooldown = commands.CooldownMapping.from_cooldown(2, 10.0, commands.BucketType.user)
    
    async def on_message(self, message):
        if message.author.bot:
            return
        
        if message.guild is not None and message.guild.id == self.settings.guild_id:
            if not self.settings.permissions.hasAtLeast(message.guild, message.author, 6):
                role_submod = message.guild.get_role(self.settings.guild().role_sub_mod)
                if role_submod is not None:
                    if role_submod not in message.author.roles:
                        if await self.filter(message):
                            return
                else:
                    if await self.filter(message):
                        return
                                
        await self.process_commands(message)

    async def process_commands(self, message):
        if message.author.bot:
            return
        
        ctx = await self.get_context(message, cls=context.Context)
        await self.invoke(ctx)

    async def filter(self, message):
        if not message.guild:
            return False
        if message.author.bot:
            return False
        guild = self.settings.guild()
        if message.guild.id != self.settings.guild_id:
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
                filter_word_without_spaces = "".join(word.word.lower().split())
                if not self.settings.permissions.hasAtLeast(message.guild, message.author, word.bypass):
                    if (word.word.lower() in folded_message) or \
                        (not word.false_positive and word.word.lower() in folded_without_spaces) or \
                        (not word.false_positive and word.word.lower() in folded_without_spaces_and_punctuation) or \
                        (not word.false_positive and filter_word_without_spaces in folded_without_spaces_and_punctuation):
                        # remove all whitespace, punctuation in message and run filter again
                        if word.false_positive and word.word.lower() not in folded_message.split():
                            continue
                        
                        dev_role = message.guild.get_role(self.settings.guild().role_dev)
                        if not (word.piracy and message.channel.id == self.settings.guild().channel_development and dev_role in message.author.roles):
                            # ignore if this is a piracy word and the channel is #development and the user has dev role
                            word_found = True
                            await self.delete(message)
                            if not reported:
                                await self.do_filter_notify(message.author, message.channel, word.word)
                                await self.ratelimit(message)
                                reported = True
                            if word.notify:
                                await self.report.report(message, message.author, word.word)
                                return True
        return word_found
    
    async def do_invite_filter(self, message):
        """
        INVITE FILTER
        """
        if message.content:
            if not self.settings.permissions.hasAtLeast(message.guild, message.author, 5):
                invites = re.findall(self.invite_filter, message.content, flags=re.S)
                if invites:
                    whitelist = self.settings.guild().filter_excluded_guilds
                    for invite in invites:
                        try:
                            invite = await self.fetch_invite(invite)

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
                                await self.report.report(message, message.author, invite, invite=invite)
                                return True

                        except discord.errors.NotFound:
                            await self.delete(message)
                            await self.ratelimit(message)
                            await self.report.report(message, message.author, invite, invite=invite)
                            return True
        return False
    
    async def do_spoiler_filter(self, message, guild):
        """
        SPOILER FILTER
        """
        if not self.settings.permissions.hasAtLeast(message.guild, message.author, 5):
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
        if not self.settings.permissions.hasAtLeast(message.guild, message.author, 5):
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

        u = await self.settings.user(id=user.id)
        mute_role = self.settings.guild().role_mute
        mute_role = ctx.guild.get_role(mute_role)

        if mute_role in user.roles or u.is_muted:
            return

        case = Case(
            _id=self.settings.guild().case_id,
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
                self.settings.tasks.schedule_unmute(user.id, time)
            except Exception:
                raise commands.BadArgument(
                    "An error occured, this user is probably already muted")

        await self.settings.inc_caseid()
        await self.settings.add_case(user.id, case)
        u = await self.settings.user(id=user.id)
        u.is_muted = True
        u.save()

        await user.add_roles(mute_role)

        log = await logger.prepare_mute_log(ctx.me, user, case)

        public_chan = ctx.guild.get_channel(self.settings.guild().channel_public)
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


bot = Bot(command_prefix=get_prefix,
                   intents=intents, allowed_mentions=mentions, case_insensitive=True)
bot.max_messages = 10000

# Here we load our extensions(cogs) listed above in [initial_extensions].
if __name__ == '__main__':
    bot.owner_id = int(os.environ.get("BOTTY_OWNER"))
    bot.remove_command("help")
    bot.report = Report(bot)
    for extension in initial_extensions:
        bot.load_extension(extension)


async def run_once_when_ready():
    await bot.wait_until_ready()

    print(
        f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')
    bot.load_extension('cogs.commands.misc.music')
    await bot.settings.load_tasks()
    print(f'Successfully logged in and booted...!')


bot.loop.create_task(run_once_when_ready())
bot.run(os.environ.get("BOTTY_TOKEN"), bot=True, reconnect=True)
