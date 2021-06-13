import traceback

import discord
from discord.ext import commands
import cogs.utils.context as context
import cogs.utils.permission_checks as permissions


class SubNews(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="subnews")
    @commands.guild_only()
    @permissions.submod_or_admin_and_up()
    async def subnews(self, ctx: context.Context, *, description: str):
        """Post a new subreddit news post (subreddit mods only).

        Example usage
        -------------
        !subnews <description here> (optionally, attach an image for file)

        Parameters
        ----------
        description : str
            Body of the news post
        """

        if not ctx.guild.id == ctx.settings.guild_id:
            return

        db = ctx.settings.guild()
        submod = ctx.guild.get_role(db.role_sub_mod)

        channel = ctx.guild.get_channel(db.channel_subnews)
        if not channel:
            raise commands.BadArgument("A subreddit news channel was not found. Contact Slim.")

        subnews = ctx.guild.get_role(db.role_sub_news)
        if not subnews:
            raise commands.BadArgument("A subreddit news role was not found. Contact Slim.")

        body = f"{subnews.mention} New Subreddit news post!\n\n{description}"
        if len(ctx.message.attachments) > 0:
            f = await ctx.message.attachments[0].to_file()
        else:
            f = None

        await channel.send(content=body, file=f, allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=True))
        await ctx.message.delete()
        await ctx.send_success("Posted subreddit news post!", delete_after=5)

    @subnews.error
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
    bot.add_cog(SubNews(bot))
