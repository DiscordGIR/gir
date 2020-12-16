import discord
from discord.ext import commands
import io
import aiohttp
import re
from enum import Enum
import traceback


class EmojiType(Enum):
    Bad = 1
    Emoji = 2
    Image = 3
    
        
class BoosterEmojis(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='auditemojis', hidden=True)
    async def auditemojis(self, ctx: commands.Context):
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 7):
            raise commands.BadArgument(
                "You need to be Aaron to use that command.")

        channel = ctx.guild.get_channel(self.bot.settings.guild().channel_booster_emoji)
        if not channel:
            return
        
        await ctx.message.delete()
        count = 0
        async for msg in channel.history():
            _type, _ = await self.get_bytes(msg)
            if _type != EmojiType.Bad:
                self.add_reactions(True, msg)
                count += 1
            else:
                self.add_reactions(False, msg)

            # emoji = custom_emojis[0]
            # byte = await emoji.url.read()
            # await channel.guild.create_custom_emoji(image=byte, name=emoji.name)
        await ctx.send(f"Found {count} emojis and added reacts for them.", delete_after=5)
        
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if not payload.member:
            return
        if not payload.member.guild:
            return
        
        channel = payload.member.guild.get_channel(payload.channel_id)
        try:
            msg = await channel.fetch_message(payload.message_id)
        except:
            return
        db = self.bot.settings
        
        if not msg.guild.id == db.guild_id:
            return
        if not payload.channel_id == db.guild().channel_booster_emoji:
            return
        if payload.channel_id != self.bot.settings.guild().channel_booster_emoji:
            return
        if not str(payload.emoji) in ['✅', '❌']:
            return
        if not self.bot.settings.permissions.hasAtLeast(payload.member.guild, payload.member, 7):
            await msg.remove_reaction(payload.emoji, payload.member)
            return

        if str(payload.emoji == '❌'):
            await msg.delete()
            return

        _type, _bytes = await self.get_bytes(msg)
        if _type == EmojiType.Bad:
            await msg.remove_reaction(payload.emoji, payload.member)
            return

        if _type == EmojiType.Emoji:
            emoji = await channel.guild.create_custom_emoji(image=_bytes, name=payload.emoji.name)
            await ctx.send(emoji)
        else:
            await self.handle_adding_image(_bytes)
            

    @commands.Cog.listener()
    async def on_message(self, msg):
        if not msg.guild:
            return
        db = self.bot.settings
        if not msg.guild.id == db.guild_id:
            return
        if not msg.channel.id == db.guild().channel_booster_emoji:
            return
        _type, _ = await self.get_bytes(msg)
        await self.add_reactions(_type != EmojiType.Bad, msg)    

    async def get_bytes(self, msg):
        custom_emojis = re.findall(r'<:\d+>|<:.+?:\d+>', msg.content)
        custom_emojis_gif = re.findall(r'<a:.+:\d+>|<:.+?:\d+>', msg.content)
        custom_emojis = [int(e.split(':')[2].replace('>', '')) for e in custom_emojis]
        custom_emojis = [f"https://cdn.discordapp.com/emojis/{e}.png?v=1" for e in custom_emojis]
        custom_emojis_gif = [f"https://cdn.discordapp.com/emojis/{e}.gif?v=1" for e in custom_emojis]
        print(custom_emojis)
        pattern = re.compile(
            r"(https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*))")
        link = pattern.search(msg.content)
        if (link):
            if link.group(0):
                link = link.group(0)

        if len(custom_emojis) > 1 or len(custom_emojis_gif) > 1 or len(msg.attachments) > 1:
            return (EmojiType.Bad, None)
        elif len(custom_emojis) == 1:
            emoji = custom_emojis[0]
            return (EmojiType.Emoji, await self.do_content_parsing(emoji))
        elif len(custom_emojis_gif) == 1:
            emoji = custom_emojis_gif[0]
            return (EmojiType.Emoji, await self.do_content_parsing(emoji))
        elif len(msg.attachments) == 1:
            url = msg.attachments[0].url
            return (EmojiType.Image, await self.do_content_parsing(url))
        elif link:
            return (EmojiType.Image, await self.do_content_parsing(link))
        else:
            return (EmojiType.Bad, None)

    async def add_reactions(good: bool, msg: discord.Message):
        if good:
            await msg.add_reaction('✅')
            await msg.add_reaction('❌')
        else:
            await msg.add_reaction('❓')

    async def do_content_parsing(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.head(url) as resp:
                if resp.status != 200:
                    return None
                elif resp.headers["CONTENT-TYPE"] in ["image/png", "image/jpeg", "image/gif", "image/webp"]:
                    return io.BytesIO(await resp.read())
                else:
                    return None
                
    @auditemojis.error
    async def info_error(self, ctx, error):
        await ctx.message.delete(delay=5)
        if (isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.BotMissingPermissions)
            or isinstance(error, commands.MissingPermissions)
                or isinstance(error, commands.NoPrivateMessage)):
            await self.bot.send_error(ctx, error)
        else:
            await self.bot.send_error(ctx, error)
            traceback.print_exc() 


def setup(bot):
    bot.add_cog(BoosterEmojis(bot))
