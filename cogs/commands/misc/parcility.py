import traceback

import discord
import re
import json
import aiohttp
from datetime import datetime
from discord.ext import commands, menus

class TweakMenu(menus.GroupByPageSource):
    async def format_page(self, menu, entry):
        entry = entry.items[0]
        embed = discord.Embed(title=entry.get('Name'), color=discord.Color.blue())
        embed.description = discord.utils.escape_markdown(entry.get('Description'))
        embed.add_field(name="Author", value= discord.utils.escape_markdown(entry.get('Author')), inline=True)
        embed.add_field(name="Version", value= discord.utils.escape_markdown(entry.get('Version')), inline=True)
        embed.add_field(name="Repo", value=f"[{entry.get('repo').get('label')}]({entry.get('repo').get('url')})", inline=True)
        embed.add_field(name="Bundle ID", value= discord.utils.escape_markdown(entry.get('Package')), inline=True)
        embed.add_field(name="More Info", value=f"[Click Here](https://parcility.co/package/{entry.get('Package')}/{entry.get('repo').get('slug')})", inline=False)
        pattern = re.compile(r"((http|https)\:\/\/)[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*")
        if (pattern.match(entry.get('Icon'))):
            embed.set_thumbnail(url=entry.get('Icon'))
        embed.set_footer(icon_url=entry.get('repo').get('icon'), text=f"{entry.get('repo').get('label')} • Page {menu.current_page +1}/{self.get_max_pages()}")
        embed.timestamp = datetime.now()
        return embed
    
class MenuPages(menus.MenuPages):
    async def update(self, payload):
        if self._can_remove_reactions:
            if payload.event_type == 'REACTION_ADD':
                await self.message.remove_reaction(payload.emoji, payload.member)
            elif payload.event_type == 'REACTION_REMOVE':
                return
        await super().update(payload)


class Parcility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.search_url = 'https://api.parcility.co/db/search?q='
        self.repo_url = 'https://api.parcility.co/db/repo/'

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild:
            return
        if not message.guild.id == self.bot.settings.guild_id:
            return

        pattern = re.compile(r'(\[(?:\[??[^\[]*?\])\])')
        check = re.compile(r'.*\S.*')
        matches = pattern.findall(message.content)
        if not matches:
            return
        search_term =  matches[0].replace('[[', '').replace(']]','')
        print(search_term)
        if not search_term or not check.match(search_term):
            return

        ctx = await self.bot.get_context(message)
        async with ctx.typing():
            response = await self.search_request(search_term)
            
        if response is None:
            embed = discord.Embed(title="Error", color=discord.Color.red())
            embed.description = "An error occurred while searching for that tweak."
            await message.delete(delay=5)
            await message.channel.send(embed=embed, delete_after=5)
            return
        elif len(response) == 0:
            embed = discord.Embed(title="Not Found", color=discord.Color.red())
            embed.description = 'Sorry, I couldn\'t find any tweaks with that name.'
            await message.delete(delay=5)
            await message.channel.send(embed=embed, delete_after=5)
            return
        
        menu = MenuPages(source=TweakMenu(
            response, key=lambda t: 1, per_page=1), clear_reactions_after=True)
        await menu.start(ctx)

    async def search_request(self, search):
        async with aiohttp.ClientSession() as client:
            async with client.get(f'{self.search_url}{search}') as resp:
                response = json.loads(await resp.text())
                #print(response)
                if response.get('code') == 404:
                    return []
                elif response.get('code') == 200:
                    return response.get('data')
                else:
                    return None
                
    @commands.command(name="repo")
    @commands.guild_only()
    async def repo(self, ctx, *, repo):
        data = await self.repo_request(repo)

        if data is None:
            print("error")
            embed = discord.Embed(title="Error", color=discord.Color.red())
            embed.description = f'An error occurred while searching for that repo'
            await ctx.message.delete(delay=5)
            await ctx.send(embed=embed, delete_after=5)
            return
        elif len(data) == 0:
            print("len")
            embed = discord.Embed(title="Not Found", color=discord.Color.red())
            embed.description = f'Sorry, I couldn\'t find a repo by that name.'
            await ctx.message.delete(delay=5)
            await ctx.send(embed=embed, delete_after=5)
            return
        
        embed = discord.Embed(title=data.get('Label'), color=discord.Color.blue())
        embed.description = data.get('Description')
        embed.add_field(name="Packages", value=data.get('package_count'), inline=False)
        embed.add_field(name="URL", value=data.get('repo'), inline=False)
        embed.add_field(name="More Info", value=f'[Click Here](https://parcility.co/{repo})', inline=False)
        embed.set_thumbnail(url=data.get('Icon'))
        embed.set_footer(text=data.get('Label'), icon_url=data.get('Icon'))
        embed.timestamp = datetime.now()

        await ctx.send(embed=embed)
        
    async def repo_request(self, repo):
        async with aiohttp.ClientSession() as client:
            async with client.get(f'{self.repo_url}{repo}') as resp:
                response = json.loads(await resp.text())
                if response.get('code') == 404:
                    return []
                elif response.get('code') == 200:
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
