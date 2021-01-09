import aiohttp
import datetime
import traceback
import typing
from io import BytesIO

import discord
from discord.ext import commands
from twemoji_parser import emoji_to_url


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spam_cooldown = commands.CooldownMapping.from_cooldown(3, 15.0, commands.BucketType.channel)

    @commands.command(name="jumbo")
    @commands.guild_only()
    async def jumbo(self, ctx, emoji: typing.Union[discord.Emoji, discord.PartialEmoji, str]):
        """Post large version of a given emoji

        Example usage
        -------------
        !jumbo :ntwerk:

        Parameters
        ----------
        emoji : typing.Union[discord.Emoji, discord.PartialEmoji]
            Emoji to post
        """
        
        bot_chan = self.bot.settings.guild().channel_botspam
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 5) and ctx.channel.id != bot_chan:
            if await self.ratelimit(ctx.message):
                raise commands.BadArgument("This command is on cooldown.")

        if isinstance(emoji, str):
            emoji_url = await emoji_to_url(emoji)
            if emoji_url == emoji :
                raise commands.BadArgument("Couldn't find a suitable emoji.")
            emoji_bytes = await self.get_emoji_bytes(emoji_url)
            if emoji_bytes is None:
                raise commands.BadArgument("Couldn't find a suitable emoji.")

            _file = discord.File(BytesIO(emoji_bytes), filename="image.png")
            await ctx.message.reply(file=_file, mention_author=False)

        else:
            await ctx.message.reply(emoji.url)

    async def get_emoji_bytes(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.head(url) as resp:
                if resp.status != 200:
                    return None
                elif resp.headers["CONTENT-TYPE"] not in ["image/png", "image/jpeg", "image/gif", "image/webp"]:
                    return None
                else:
                    async with session.get(url) as resp2:
                        if resp2.status != 200:
                            return None

                        return await resp2.read()

    async def ratelimit(self, message):
        bucket = self.spam_cooldown.get_bucket(message)
        return bucket.update_rate_limit()

    @commands.command(name="avatar")
    @commands.guild_only()
    async def avatar(self, ctx, member: discord.Member = None):
        """Post large version of a given user's avatar

        Parameters
        ----------
        member : discord.Member, optional
            Member to get avatar of, default to command invoker
        """

        if member is None:
            member = ctx.author

        bot_chan = self.bot.settings.guild().channel_botspam

        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 5) and ctx.channel.id != bot_chan:
            raise commands.BadArgument(
                f"Command only allowed in <#{bot_chan}>")

        await ctx.message.delete()
        embed = discord.Embed(title=f"{member}'s avatar")
        embed.set_image(url=member.avatar_url)
        embed.color = discord.Color.random()
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)

    @jumbo.error
    @avatar.error
    async def info_error(self, ctx, error):
        await ctx.message.delete(delay=5)
        if (isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.MissingPermissions)
            or isinstance(error, commands.BotMissingPermissions)
            or isinstance(error, commands.MaxConcurrencyReached)
                or isinstance(error, commands.NoPrivateMessage)):
            await self.bot.send_error(ctx, error)
        else:
            await self.bot.send_error(ctx, "A fatal error occured. Tell <@109705860275539968> about this.")
            traceback.print_exc()


def setup(bot):
    bot.add_cog(Misc(bot))
