import traceback

import datetime
import asyncio
import cogs.utils.permission_checks as permissions
import cogs.utils.context as context
import discord
from discord.ext import commands


class Genius(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="commonissue")
    @commands.guild_only()
    @permissions.genius_and_up()
    @commands.max_concurrency(1, per=commands.BucketType.member, wait=False)
    async def commonissue(self, ctx: context.Context, *, title: str):
        """Submit a new common issue (Geniuses only)

        Example use:
        ------------
        !commonissue This is a title (you will be prompted for a description)

        Parameters
        ----------
        title : str
            Title for the issue

        """

        if not ctx.guild.id == ctx.settings.guild_id:
            return

        channel = ctx.guild.get_channel(ctx.settings.guild().channel_common_issues)
        if not channel:
            return

        prompt = context.PromptData(
            value_name="description",
            description="Please enter a description for this common issue.",
            convertor=str)
        description = await ctx.prompt(prompt)
        
        if description is None:
            await ctx.message.delete(delay=5)
            await ctx.send_warning("Cancelled new common issue.", delete_after=5)
            return
        
        embed, f = await self.prepare_issues_embed(title, description, ctx.message)
        await channel.send(embed=embed, file=f)
        await ctx.send_success("Common issue posted!", delete_after=5)
        await ctx.message.delete(delay=5)
        
    @commands.command(name="postembed")
    @commands.guild_only()
    @permissions.genius_and_up()
    @commands.max_concurrency(1, per=commands.BucketType.member, wait=False)
    async def postembed(self, ctx: context.Context, *, title: str):
        """Post an embed in the current channel (Geniuses only)

        Example use:
        ------------
        !postembed This is a title (you will be prompted for a description)

        Parameters
        ----------
        title : str
            Title for the embed
        
        """

        if not ctx.guild.id == ctx.settings.guild_id:
            return

        channel = ctx.channel
        
        prompt = context.PromptData(
            value_name="description",
            description="Please enter a description for this embed.",
            convertor=str)
        description = await ctx.prompt(prompt)
        
        if description is None:
            await ctx.message.delete(delay=5)
            await ctx.send_warning("Cancelled embed post.", delete_after=5)
            return

        embed, f = await self.prepare_issues_embed(title, description, ctx.message)
        await channel.send(embed=embed, file=f)
        await ctx.message.delete()

    async def prepare_issues_embed(self, title, description, message):
        embed = discord.Embed(title=title)
        embed.color = discord.Color.random()
        embed.description = description
        f = None
        if len(message.attachments) > 0:
            f = await message.attachments[0].to_file()
            embed.set_image(url=f"attachment://{f.filename}")
        embed.set_footer(text=f"Submitted by {message.author}")
        embed.timestamp = datetime.datetime.now()
        return embed, f

    @postembed.error
    @commonissue.error
    async def info_error(self, ctx: context.Context, error):
        await ctx.message.delete(delay=5)
        if (isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, permissions.PermissionsFailure)
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.MissingPermissions)
            or isinstance(error, commands.BotMissingPermissions)
            or isinstance(error, commands.MaxConcurrencyReached)
                or isinstance(error, commands.NoPrivateMessage)):
            await ctx.send_error(error)
        else:
            await ctx.send_error("A fatal error occured. Tell <@109705860275539968> about this.")
            traceback.print_exc()


def setup(bot):
    bot.add_cog(Genius(bot))
