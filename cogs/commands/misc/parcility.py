import traceback

import discord
import re
import json
import aiohttp
import urllib
from datetime import datetime
import cogs.utils.permission_checks as permissions
import cogs.utils.context as context
from discord.ext import commands, menus
from yarl import URL

package_url = 'https://api.parcility.co/db/package/'
search_url = 'https://api.parcility.co/db/search?q='

async def package_request(package):
    async with aiohttp.ClientSession() as client:
        async with client.get(URL(f'{package_url}{package.get("Package")}', encoded=True)) as resp:
            if resp.status == 200:
                response = json.loads(await resp.text())
                if response.get('code') == 200:
                    package["Price"] = response['data'].get("Price")
            else:
                return None
    return package


async def search_request(search):
    async with aiohttp.ClientSession() as client:
        async with client.get(URL(f'{search_url}{urllib.parse.quote(search)}', encoded=True)) as resp:
            if resp.status == 200:
                response = json.loads(await resp.text())
                if response.get('code') == 404:
                    return []
                elif response.get('code') == 200:
                    return response.get('data')
                else:
                    return None
            else:
                return None

async def aiter(packages):
    for package in packages:
        p = await package_request(package)
        yield p

class TweakMenu(menus.AsyncIteratorPageSource):
    def __init__(self, response, length):
        super().__init__(response, per_page=1)
        self.page_length = length
        
    async def format_page(self, menu, entry):
        entry = await package_request(entry)
        embed = discord.Embed(title=entry.get('Name'), color=discord.Color.blue())
        embed.description = discord.utils.escape_markdown(entry.get('Description'))
        embed.add_field(name="Author", value= discord.utils.escape_markdown(entry.get('Author') or "No author"), inline=True)
        embed.add_field(name="Version", value= discord.utils.escape_markdown(entry.get('Version') or "No version"), inline=True)
        embed.add_field(name="Price", value=entry.get("Price") or "Free")
        embed.add_field(name="Repo", value=f"[{entry.get('repo').get('label')}]({entry.get('repo').get('url')})" or "No repo", inline=True)
        if entry.get('repo').get('isDefault') is False:
            embed.add_field(name="Add Repo", value=f"[Click Here](https://sharerepo.stkc.win/?repo={entry.get('repo').get('url')})" or "No repo", inline=True)
        embed.add_field(name="More Info", value=f"[View on Parcility](https://parcility.co/package/{entry.get('Package')}/{entry.get('repo').get('slug')})", inline=False)
        pattern = re.compile(r"((http|https)\:\/\/)[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*")
        if (pattern.match(entry.get('Icon'))):
            embed.set_thumbnail(url=entry.get('Icon'))
        embed.set_footer(icon_url=entry.get('repo').get('icon'), text=discord.utils.escape_markdown(entry.get('Package'))+f" • Page {menu.current_page +1}/{self.page_length}" or "No package")
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
        self.repo_url = 'https://api.parcility.co/db/repo/'

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None:
            return
        if not message.guild.id == self.bot.settings.guild_id:
            return
        
        author = message.guild.get_member(message.author.id)
        if author is None:
            return
        
        if not self.bot.settings.permissions.hasAtLeast(message.guild, author, 5) and message.channel.id == self.bot.settings.guild().channel_general:
            return
        
        pattern = re.compile(r".*?(?<!\[)+\[\[((?!\s+)([\w+\ \&\+\-]){2,})\]\](?!\])+.*")
        if not pattern.match(message.content):
            return
        
        matches = pattern.findall(message.content)
        if not matches:
            return

        search_term =  matches[0][0].replace('[[', '').replace(']]','')
        if not search_term:
            return

        ctx = await self.bot.get_context(message, cls=context.Context)
        async with ctx.typing():
            response = await search_request(search_term)
        
        if response is None:
            await ctx.send_error("An error occurred while searching for that tweak.")
            return
        elif len(response) == 0:
            await ctx.send_error("Sorry, I couldn't find any tweaks with that name.")
            return
       
        menu = MenuPages(source=TweakMenu(aiter(response), len(response)), clear_reactions_after=True)
        await menu.start(ctx)
    
    @commands.command(name="repo")
    @permissions.no_general_unless_mod()
    @commands.guild_only()
    async def repo(self,  ctx: context.Context, *, repo):
        
        data = await self.repo_request(repo)
        repourl = data.get('repo')

        if data is None:
            embed = discord.Embed(title="Error", color=discord.Color.red())
            embed.description = f'An error occurred while searching for that repo'
            await ctx.message.delete(delay=5)
            await ctx.send(embed=embed, delete_after=5)
            return
        elif len(data) == 0:
            embed = discord.Embed(title="Not Found", color=discord.Color.red())
            embed.description = f'Sorry, I couldn\'t find a repo by that name.'
            await ctx.message.delete(delay=5)
            await ctx.send(embed=embed, delete_after=5)
            return
        
        embed = discord.Embed(title=data.get('Label'), color=discord.Color.blue())
        embed.description = data.get('Description')
        embed.add_field(name="Packages", value=data.get('package_count'), inline=True)
        embed.add_field(name="Sections", value=data.get('section_count'), inline=True)
        embed.add_field(name="URL", value=data.get('url'), inline=False)
        if data.get('isDefault') is False:
            embed.add_field(name="Add Repo", value=f'[Click Here](https://sharerepo.stkc.win/?repo={data.get("url")})', inline=True)
        embed.add_field(name="More Info", value=f'[View on Parcility](https://parcility.co/{data.get("id")})', inline=False)
        embed.set_thumbnail(url=data.get('Icon'))
        if data.get('isDefault') == True:
            embed.set_footer(text='Default Repo')
        embed.timestamp = datetime.now()

        await ctx.send(embed=embed)
        
    async def repo_request(self, repo):
        async with aiohttp.ClientSession() as client:
            async with client.get(f'{self.repo_url}{repo}') as resp:
                if resp.status == 200:
                    response = json.loads(await resp.text())
                    if response.get('code') == 404:
                        return []
                    elif response.get('code') == 200:
                        return response.get('data')
                    else:
                        return None
                else:
                    return None
                
                
    @repo.error
    async def info_error(self,  ctx: context.Context, error):
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
    bot.add_cog(Parcility(bot))
