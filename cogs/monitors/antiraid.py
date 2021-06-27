import string
from asyncio import sleep
from datetime import datetime, timezone
from re import U

import cogs.utils.logs as logger
import cogs.utils.context as context
import discord
from data.case import Case
from discord.ext import commands
from expiringdict import ExpiringDict
from fold_to_ascii import fold


class RaidType:
    PingSpam = 1
    RaidPhrase = 2
    MessageSpam = 3

class AntiRaidMonitor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.join_raid_detection_threshold = commands.CooldownMapping.from_cooldown(10, 8, commands.BucketType.guild)
        self.raid_detection_threshold = commands.CooldownMapping.from_cooldown(4, 15.0, commands.BucketType.guild)
        self.message_spam_detection_threshold = commands.CooldownMapping.from_cooldown(7, 5.0, commands.BucketType.member)
        # self.message_spam_detection_threshold = MessageCooldownMapping.from_cooldown(4, 8, BucketType.message)

        self.raid_alert_cooldown = commands.CooldownMapping.from_cooldown(1, 600.0, commands.BucketType.guild)
        
        self.spam_user_mapping = ExpiringDict(max_len=100, max_age_seconds=10)
        self.join_user_mapping = ExpiringDict(max_len=100, max_age_seconds=10)
        self.ban_user_mapping = ExpiringDict(max_len=100, max_age_seconds=120)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id != self.bot.settings.guild_id:
            return
        if member.bot:
            return
        
        current = datetime.now().timestamp()
        join_spam_detection_bucket = self.join_raid_detection_threshold.get_bucket(member)
        self.join_user_mapping[member.id] = member
        
        if join_spam_detection_bucket.update_rate_limit(current):
            users = list(self.join_user_mapping.keys())
            for user in users:
                try:
                    user = self.join_user_mapping[user]
                except KeyError:
                    continue
                
                if user in self.ban_user_mapping:
                    continue
                
                try:
                    await self.raid_ban(user, reason="Join spam detected")
                except Exception:
                    pass
                
            raid_alert_bucket = self.raid_alert_cooldown.get_bucket(user)
            if not raid_alert_bucket.update_rate_limit(current):
                await self.bot.reports.report_raid(user)
                await self.freeze_server(member.guild)
                
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild:
            return
        if message.author.bot:
            return
        if message.guild.id != self.bot.settings.guild_id:
            return
        if self.bot.settings.permissions.hasAtLeast(message.guild, message.author, 5):
            return
        
        if await self.ping_spam(message):  
            await self.handle_raid_detection(message, RaidType.PingSpam)
        elif await self.raid_phrase_detected(message):
            await self.handle_raid_detection(message, RaidType.RaidPhrase)
        elif await self.message_spam(message):
            await self.handle_raid_detection(message, RaidType.MessageSpam)

    async def handle_raid_detection(self, message: discord.Message, raid_type: RaidType):
        current = message.created_at.replace(tzinfo=timezone.utc).timestamp()
        spam_detection_bucket = self.raid_detection_threshold.get_bucket(message)
        ctx = await self.bot.get_context(message, cls=context.Context)
        user = message.author
        
        do_freeze = False
        do_banning = False
        self.spam_user_mapping[user.id] = 1
        
        # has the antiraid filter been triggered 5 or more times in the past 10 seconds?
        if spam_detection_bucket.update_rate_limit(current):
            do_banning = True
            # yes! notify the mods and lock the server.
            raid_alert_bucket = self.raid_alert_cooldown.get_bucket(message)
            if not raid_alert_bucket.update_rate_limit(current):
                await self.bot.reports.report_raid(user, message)
                do_freeze = True


        # lock the server
        if do_freeze:
            await self.freeze_server(message.guild)

        if raid_type in [RaidType.PingSpam, RaidType.MessageSpam]:
            if not do_banning and not do_freeze:
                if raid_type is RaidType.PingSpam:
                    title = "Ping spam detected"
                else:
                    title = "Message spam detected"
                await self.bot.reports.report_spam(message, user, title=title)
            else:
                users = list(self.spam_user_mapping.keys())
                for user in users:
                    try:
                        _ = self.spam_user_mapping[user]
                    except KeyError:
                        continue
                    
                    if user in self.ban_user_mapping:
                        continue
                    
                    user = message.guild.get_member(user)
                    if user is None:
                        continue
                    
                    try:
                        await self.raid_ban(user, reason="Ping spam detected")
                    except Exception:
                        pass

    async def ping_spam(self, message):
        if len(set(message.mentions)) > 4 or len(set(message.role_mentions)) > 2:
            mute = self.bot.get_command("mute")
            if mute is not None:
                ctx = await self.bot.get_context(message, cls=context.Context)
                user = message.author
                ctx.message.author = ctx.author = ctx.me
                await mute(ctx=ctx, user=user, reason="Ping spam")
                ctx.message.author = ctx.author = user
                return True

        return False
    
    async def message_spam(self, message):
        if self.bot.settings.permissions.hasAtLeast(message.guild, message.author, 1):
            return False
                
        bucket = self.message_spam_detection_threshold.get_bucket(message)
        current = message.created_at.replace(tzinfo=timezone.utc).timestamp()

        if bucket.update_rate_limit(current):
            if message.author.id in self.spam_user_mapping:
                return True
            
            mute = self.bot.get_command("mute")
            if mute is not None:
                ctx = await self.bot.get_context(message, cls=context.Context)
                user = message.author
                ctx.message.author = ctx.author = ctx.me
                try:
                    await mute(ctx=ctx, user=user, reason="Message spam")
                except Exception:
                    pass
                ctx.message.author = ctx.author = user
                return True
    
    async def raid_phrase_detected(self, message):
        if self.bot.settings.permissions.hasAtLeast(message.guild, message.author, 2):
            return False

        #TODO: Unify filtering system
        symbols = (u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
                u"abBrdeex3nnKnmHonpcTyoxu4wwbbbeoRABBrDEEX3NNKNMHONPCTyOXU4WWbbbEOR")

        tr = {ord(a): ord(b) for a, b in zip(*symbols)}

        folded_message = fold(message.content.translate(tr).lower()).lower()
        folded_without_spaces = "".join(folded_message.split())
        folded_without_spaces_and_punctuation = folded_without_spaces.translate(str.maketrans('', '', string.punctuation))

        if folded_message:
            for word in self.bot.settings.guild().raid_phrases:
                if not self.bot.settings.permissions.hasAtLeast(message.guild, message.author, word.bypass):
                    if (word.word.lower() in folded_message) or \
                        (not word.false_positive and word.word.lower() in folded_without_spaces) or \
                        (not word.false_positive and word.word.lower() in folded_without_spaces_and_punctuation):
                        # remove all whitespace, punctuation in message and run filter again
                        if word.false_positive and word.word.lower() not in folded_message.split():
                            continue

                        ctx = await self.bot.get_context(message, cls=context.Context)
                        await self.raid_ban(message.author)
                        return True
        return False
            
    async def raid_ban(self, user: discord.Member, reason="Raid phrase detected"):
        case = Case(
            _id=self.bot.settings.guild().case_id,
            _type="BAN",
            date=datetime.now(),
            mod_id=self.bot.user.id,
            mod_tag=str(self.bot),
            punishment="PERMANENT",
            reason=reason
        )

        await self.bot.settings.inc_caseid()
        await self.bot.settings.add_case(user.id, case)
        
        continue_ = False
        try:
            _ = self.ban_user_mapping[user.id]
        except KeyError:
            continue_ = True
            
        if not continue_:
            return
        
        self.ban_user_mapping[user.id] = 1
        await user.ban(reason="Raid")

        log = await logger.prepare_ban_log(self.bot.user, user, case)
        public_logs = user.guild.get_channel(self.bot.settings.guild().channel_public)
        if public_logs:
            log.remove_author()
            log.set_thumbnail(url=user.avatar_url)
            await public_logs.send(embed=log)

    async def freeze_server(self, guild):
        settings = self.bot.settings.guild()
        
        for channel in settings.locked_channels:
            channel = guild.get_channel(channel)
            if channel is None:
                continue
            
            default_role = guild.default_role
            member_plus = guild.get_role(settings.role_memberplus)   
            
            default_perms = channel.overwrites_for(default_role)
            memberplus_perms = channel.overwrites_for(member_plus)

            if default_perms.send_messages is None and memberplus_perms.send_messages is None:
                default_perms.send_messages = False
                memberplus_perms.send_messages = True

                try:
                    await channel.set_permissions(default_role, overwrite=default_perms, reason="Locked!")
                    await channel.set_permissions(member_plus, overwrite=memberplus_perms, reason="Locked!")
                except Exception:
                    pass


def setup(bot):
    bot.add_cog(AntiRaidMonitor(bot))
