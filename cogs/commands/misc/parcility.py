import traceback

import discord
import re
import json
import aiohttp
from discord.ext import commands


class Parcility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.search_url = 'https://api.parcility.co/db/search?q='

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild:
            return
        if not message.guild.id == self.bot.settings.guild_id:
            return

        # pattern = re.compile(r'(\[(?:\[??[^\[]*?\])\])')
        pattern = re.compile(r'(\[(?:\[??[^\[]*?\])\])')
        check = re.compile(r'.*\S.*')
        matches = pattern.match(message.content)
        if not matches:
            return
        search_term =  message.content.replace('[[', '').replace(']]','')
        if not search_term or not check.match(search_term):
            return

        response = await self.search_request(search_term)
        
        if response is None:
            await message.channel.send("error")
            return
        elif len(response) == 0:
            await message.channel.send("not found")
            return
            
        # here you'd pretty up the results etc etc, use discord.ext.paginate,
        # see other files for some examples if you need
        await message.channel.send(", ".join([r.get('Name') for r in response]))
        
    async def search_request(self, search):
        async with aiohttp.ClientSession() as client:
            async with client.get(f'{self.search_url}{search}') as resp:
                response = json.loads(await resp.text())
                print(response)
                if response.get('code') == 404:
                    return []
                elif response.get('code') == 200:
                    return response.get('data')
                else:
                    return None
                
    @commands.command(name="repo")
    @commands.guild_only()
    async def repo(self, ctx, *, repo):
        pass
        
    async def repo_request(self):
        async with aiohttp.ClientSession() as client:
            async with client.get(self.repo_url) as resp:
                response = json.loads(await resp.text())
                if response.get('code') == 200:
                    return response.get('data')
                else:
                    return None
                
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
    bot.add_cog(Parcility(bot))
