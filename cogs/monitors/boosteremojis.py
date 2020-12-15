import discord
from discord.ext import commands
import io
import aiohttp
import re
import traceback

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
            if await self.audit_msg(msg):
                count += 1
            # emoji = custom_emojis[0]
            # byte = await emoji.url.read()
            # await channel.guild.create_custom_emoji(image=byte, name=emoji.name)
        await ctx.send(f"Found {count} emojis and added reacts for them.", delete_after=5)
        
    async def on_raw_reaction_add(self, payload):
        if payload.channel_id != self.bot.settings.guild().channel_booster_emoji:
            return
        if not self.bot.settings.permissions.hasAtLeast(payload.member.guild, payload.member, 7):
            return
        if not str(payload.emoji) in ['✅', '❌']:
            return
        
    async def audit_msg(self, msg):
        custom_emojis = re.findall(r'<a:.+?:\d+>|<:.+?:\d+>', msg.content)
        custom_emojis = [int(e.split(':')[2].replace('>', '')) for e in custom_emojis]
        custom_emojis = [self.bot.get_emoji(e) for e in custom_emojis]

        pattern = re.compile(
            r"(https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*))")
        link = pattern.search(msg.content)
        if (link):
            if link.group(0):
                link = link.group(0)

        if len(custom_emojis) > 1 or len(msg.attachments) > 1:
            await msg.add_reaction('❓')
            return False
        elif len(custom_emojis) == 1:
            await msg.add_reaction('✅')
            await msg.add_reaction('❌')
            return True
        elif len(msg.attachments) == 1:
            url = msg.attachments[0].url
            if await self.do_content_parsing(url) is None:
                await msg.add_reaction('❓')
                return False
            else:
                await msg.add_reaction('✅')
                await msg.add_reaction('❌')
                return True
        elif link:
            print(link)
            if await self.do_content_parsing(link) is None:
                await msg.add_reaction('❓')
            else:
                count += 1
                await msg.add_reaction('✅')
                await msg.add_reaction('❌')
                return True
        else:
            await msg.add_reaction('❓')
            return False
                    
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
