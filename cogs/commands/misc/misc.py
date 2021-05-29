import datetime
import json
import os
import re
import traceback
import typing
from io import BytesIO

import aiohttp
import discord
import humanize
import pytimeparse
import cogs.utils.permission_checks as permissions
from discord.ext import commands
from twemoji_parser import emoji_to_url


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spam_cooldown = commands.CooldownMapping.from_cooldown(3, 15.0, commands.BucketType.channel)

        self.CIJ_KEY = os.environ.get("CIJ_KEY")
        self.cij_baseurl = "https://canijailbreak2.com/v1/pls"
        self.devices_url = "https://api.ipsw.me/v4/devices"
        
    @commands.command(name="remindme")
    @commands.guild_only()
    @permissions.bot_channel_only_unless_mod()
    async def remindme(self, ctx, dur: str, *, reminder: str):
        """Send yourself a reminder after a given time gap

        Example usage
        -------------
        !remindme 1h bake the cake

        Parameters
        ----------
        dur : str
            After when to send the reminder
        reminder : str
            What to remind you of
        """
        
        now = datetime.datetime.now()
        delta = pytimeparse.parse(dur)
        if delta is None:
            raise commands.BadArgument("Please give a valid time to remind you! (i.e 1h, 30m)")
        
        time = now + datetime.timedelta(seconds=delta)
        if time < now:
            raise commands.BadArgument("Time has to be in the future >:(")
        reminder = discord.utils.escape_markdown(reminder)
        
        self.bot.settings.tasks.schedule_reminder(ctx.author.id, reminder, time)        
        natural_time =  humanize.naturaldelta(
                    delta, minimum_unit="seconds")
        embed = discord.Embed(title="Reminder set", color=discord.Color.random(), description=f"We'll remind you in {natural_time} ")
        await ctx.message.delete(delay=5)
        await ctx.message.reply(embed=embed, delete_after=10)
        
    @commands.command(name="jumbo")
    @permissions.bot_channel_only_unless_mod()
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
            await ctx.message.reply(emoji.url, mention_author=False)

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

    @commands.command(name="avatar", aliases=["pfp"])
    @commands.guild_only()
    @permissions.bot_channel_only_unless_mod()
    async def avatar(self, ctx, member: discord.Member = None):
        """Post large version of a given user's avatar

        Parameters
        ----------
        member : discord.Member, optional
            Member to get avatar of, default to command invoker
        """

        if member is None:
            member = ctx.author

        await ctx.message.delete()
        embed = discord.Embed(title=f"{member}'s avatar")
        embed.set_image(url=member.avatar_url)
        embed.color = discord.Color.random()
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)

    @commands.command(name="cij", aliases=['jelbrek'])
    @commands.cooldown(2, 10, commands.BucketType.member)
    @commands.guild_only()
    async def cij(self, ctx, version: str, *, device: str):
        """Check if your device is jailbreakable

        Example usage
        -------------
        !cij 13.7 iPhone 8
        !cij 14.0 iPad Pro <screensize> <generation>

        Parameters
        ----------
        version : str
            iOS/iPadOS version
        device : str
            Name of the device
        """
        
        device = await self.device_name(device)

        if device is None:
            raise commands.BadArgument("Invalid device provided.\nReminder: the usage is `!cij <iOS> <device>`")
        
        async with aiohttp.ClientSession(headers={"Authorization": self.CIJ_KEY}) as session:
            async with session.get(f"{self.cij_baseurl}/{device}/{version}") as resp:
                if resp.status == 200:
                    response = json.loads(await resp.text())
                    if response['status'] == 0:
                        if len(response['jelbreks']) > 0:
                            embed = await self.prepare_jailbreak_embed(response['jelbreks'], device, version)
                        else:
                            embed = discord.Embed(description="Unfortunately, your device is not currently jailbreakable.", footer="Note: legacy jailbreaks below iOS 6 are currently unsupported!", color=discord.Color.red())
                        await ctx.message.reply(embed=embed, delete_after=30, mention_author=False)
                        await ctx.message.delete(delay=30)
                    elif response['status'] == 1:
                        raise commands.BadArgument("Seems like you gave a valid device but the API didn't recognize it!")
                    elif response['status'] == 2:
                        raise commands.BadArgument("This device doesn't support that version of iOS!")
                    else:
                        raise commands.BadArgument("API error: device not found!")
                else:
                    raise commands.BadArgument("Catastrophic API error!")
        
    async def prepare_jailbreak_embed(self, jailbreaks, device, ios):
        embed = discord.Embed(title="Good news! Your device is jailbreakable!")
        embed.description = f"{device} on iOS {ios}"
        embed.color = discord.Color.green()
        for jailbreak in jailbreaks:
            embed.add_field(name=jailbreak['name'], value=f"*{jailbreak['type']}*\n[Link for more info]({jailbreak['url']})\nSupported on iOS versions {jailbreak['minIOS']}-{jailbreak['maxIOS']}")
        
        embed.set_footer(text="Powered by https://canijailbreak2.com from mass1ve-err0r")
        return embed
    
    async def device_name(self, device):
        device = device.lower()
        device = device.replace('s plus', '+')
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.devices_url) as resp:
                if resp.status == 200:
                    data = await resp.text()
                    devices = json.loads(data)
                    for d in devices:
                        name = re.sub(r'\((.*?)\)', "", d["name"])
                        name = name.strip()
                        name = name.replace('4[S]', '4S')
                        if name.lower() == device:
                            fix_casing = {'5s': '5S', '6s': '6S', '+': ' Plus'}
                            for test in fix_casing:
                                name = name.replace(test, fix_casing[test])

                            return name
        return None
        
    @cij.error
    @jumbo.error
    @remindme.error
    @avatar.error
    async def info_error(self, ctx, error):
        await ctx.message.delete(delay=5)
        if (isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, permissions.PermissionsFailure)
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
