import discord
from discord.ext import commands
from fold_to_ascii import fold
from data.case import Case
from datetime import datetime
import cogs.utils.logs as logger
from fold_to_ascii import fold
from cogs.monitors.report import report_raid_phrase
import string

class AntiRaid(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
            # mute = self.bot.get_command("mute")
            # if mute is not None:
            #     ctx = await self.bot.get_context(message, cls=commands.Context)
            #     user = message.author
            #     ctx.message.author = ctx.author = ctx.me
            #     await mute(ctx, user, "Ping spam")
            ctx = await self.bot.get_context(message, cls=commands.Context)
            await self.ping_spam_mute(ctx, message.author)
            await report_ping_spam(self.bot, message, message.author)
        
        #TODO: Unify filtering system
        symbols = (u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
                   u"abBrdeex3nnKnmHonpcTyoxu4wwbbbeoRABBrDEEX3NNKNMHONPCTyOXU4WWbbbEOR")

        tr = {ord(a): ord(b) for a, b in zip(*symbols)}

        folded_message = fold(message.content.translate(tr).lower()).lower()
        folded_without_spaces = "".join(folded_message.split())
        folded_without_spaces_and_punctuation = folded_without_spaces.translate(str.maketrans('', '', string.punctuation))
        word_found = False

        if folded_message:
            for word in self.bot.settings.guild().raid_phrases:
                if not self.bot.settings.permissions.hasAtLeast(message.guild, message.author, word.bypass):
                    if (word.word.lower() in folded_message) or \
                        (not word.false_positive and word.word.lower() in folded_without_spaces) or \
                        (not word.false_positive and word.word.lower() in folded_without_spaces_and_punctuation):
                        # remove all whitespace, punctuation in message and run filter again
                        if word.false_positive and word.word.lower() not in folded_message.split():
                            continue
                        
                        dev_role = message.guild.get_role(self.bot.settings.guild().role_dev)
                        print("FOUND")
                        if not (word.piracy and message.channel.id == self.bot.settings.guild().channel_development and dev_role in message.author.roles):
                            # ignore if this is a piracy word and the channel is #development and the user has dev role
                            word_found = True
                            await message.delete()
                            if word.notify:
                                await report_raid_phrase(self.bot, message.author, message, word.word)
                                return True

    async def ping_spam(self, message):
        return len(set(message.mentions)) > 4
            

    async def ping_spam_mute(self, ctx: commands.Context, user: discord.Member) -> None:
        u = await self.bot.settings.user(id=user.id)
        mute_role = self.bot.settings.guild().role_mute
        mute_role = ctx.guild.get_role(mute_role)

        if mute_role in user.roles or u.is_muted:
            return

        case = Case(
            _id=self.bot.settings.guild().case_id,
            _type="MUTE",
            date=datetime.now(),
            mod_id=ctx.me.id,
            mod_tag=str(ctx.me),
            reason="Ping spam",
            punishment="PERMANENT"
        )

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
    
    async def raid_phrase_ban(self, ctx: commands.Context, user: discord.Member):
        if self.bot.permissions.hasAtLeast(ctx.guild, ctx.author, 1):
            return
        
        case = Case(
            _id=self.bot.settings.guild().case_id,
            _type="BAN",
            date=datetime.now(),
            mod_id=ctx.me.id,
            mod_tax=str(ctx.me),
            punishment="PERMANENT",
            reason="Raid"
        )

        await self.bot.settings.inc_caseid()
        await self.bot.settings.add_case(user.id, case)
        
        await user.ban(reason="Raid")

        log = logger.prepare_ban_log(ctx.me, user, case)
        public_logs = ctx.guild.get_channel(self.bot.settings.guild().channel_public)
        if public_logs:
            log.remove_author()
            log.set_thumbnail(url=user.avatar_url)
            await public_logs.send(embed=log)

    # async def ratelimit(self, message):
    #     current = message.created_at.replace(tzinfo=datetime.timezone.utc).timestamp()

    #     bucket = self.spam_cooldown.get_bucket(message)
    #     if bucket.update_rate_limit(current):
    #         ctx = await self.get_context(message, cls=commands.Context)
    #         await self.mute(ctx, message.author)

def setup(bot):
    bot.add_cog(AntiRaid(bot))
