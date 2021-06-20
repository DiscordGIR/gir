import string
import traceback

import discord
import cogs.utils.context as context
from discord.ext import commands
from fold_to_ascii import fold


class FilterMonitor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_edit(self, _: discord.Message, after: discord.Message):
        await self.bot.filter(after)

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
        pending_task = self.bot.report.pending_tasks.get(message.id)
        if pending_task is not None:
            self.bot.report.pending_tasks[message.id] = "TERMINATE"
            

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


   
    async def info_error(self,  ctx: context.Context, error):
        if (isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.MissingPermissions)
                or isinstance(error, commands.NoPrivateMessage)):
            await ctx.send_error(error)
        else:
            traceback.print_exc()


def setup(bot):
    bot.add_cog(FilterMonitor(bot))
