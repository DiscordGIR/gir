import datetime
import os
import traceback

import cogs.utils.context as context
import cogs.utils.permission_checks as permissions
import discord
from discord.ext import commands

"""
Make sure to add the cog to the initial_extensions list
in main.py
"""

class Talkboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.question_id = os.environ.get("TB_QUESTIONS_CHANNEL")
        if self.question_id is None:
            raise Exception("Talkboard question channel ID not defined in cogs.commands.misc.talkboard.")

        self.question_ask_id = os.environ.get("TB_QUESTIONS_ASKING_CHANNEL")
        if self.question_ask_id is None:
            raise Exception("Talkboard question asking channel ID not defined in cogs.commands.misc.talkboard.")
        
        self.spam_cooldown = commands.CooldownMapping.from_cooldown(1, 90.0, commands.BucketType.user)

    @commands.guild_only()
    @commands.command()
    async def question(self, ctx: context.Context, *, message: str):
        await ctx.message.delete(delay=5)
        
        bucket = self.spam_cooldown.get_bucket(ctx.message)
        current = ctx.message.created_at.replace(tzinfo=datetime.timezone.utc).timestamp()
        if bucket.update_rate_limit(current):
            raise commands.BadArgument("You can ask 1 question every 90 seconds.")


        question_channel = ctx.guild.get_channel(int(self.question_id))
        if question_channel is None:
            raise commands.BadArgument("Question channel not found.")
        
        question_asking_channel = ctx.guild.get_channel(int(self.question_ask_id))
        if question_asking_channel is None:
            raise commands.BadArgument("Question asking channel not found.")
        
        if ctx.channel is not question_asking_channel:
            raise commands.BadArgument(f"Please ask your question in {question_asking_channel.mention}.")
        
        roles = [ ctx.settings.guild().role_genius, ctx.settings.guild().role_dev, ctx.settings.guild().role_memberpro]
        roles = [ ctx.guild.get_role(role) for role in roles ]
        
        top_role_color = None
        for role in roles:
            if role in ctx.author.roles:
                top_role_color = role.color
                break

        top_role_color = top_role_color or 0xffffff

        em = discord.Embed(description=message, color = top_role_color)
        em.set_author(name=f"Question from {ctx.author}", icon_url=ctx.author.avatar_url)
        await question_channel.send(embed=em)
        await ctx.send_success(description=f"Your question has been submitted to {question_channel.mention}!", delete_after=5)


    @question.error
    async def info_error(self, ctx: context.Context, error):
        if (isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, permissions.PermissionsFailure)
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.MissingPermissions)
            or isinstance(error, commands.BotMissingPermissions)
            or isinstance(error, commands.CommandOnCooldown)
            or isinstance(error, commands.MaxConcurrencyReached)
                or isinstance(error, commands.NoPrivateMessage)):
            await ctx.send_error(error)
        else:
            await ctx.send_error("A fatal error occured. Tell <@109705860275539968> about this.")
            traceback.print_exc()


def setup(bot):
    bot.add_cog(Talkboard(bot))
