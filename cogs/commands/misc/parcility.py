import traceback

import discord
import re
import json
import aiohttp
from datetime import datetime
from discord.ext import commands, menus

class TweakMenu(menus.Menu):
    def __init__(self, data):
        super().__init__(timeout=60.0, clear_reactions_after=True, check_embeds=True)
        self.data = data
        self.index = 0

    async def post_embed(self, message=None, channel=None):
        embed = discord.Embed(title=self.data[self.index].get('Name'), color=discord.Color.blue())
        embed.description = self.data[self.index].get('Description')
        embed.add_field(name="Author", value=self.data[self.index].get('Author'), inline=True)
        embed.add_field(name="Version", value=self.data[self.index].get('Version'), inline=True)
        embed.add_field(name="Bundle ID", value=self.data[self.index].get('Package'), inline=True)
        embed.add_field(name="Repo", value=f"[{self.data[self.index].get('repo').get('label')}]({self.data[self.index].get('repo').get('url')})", inline=False)
        embed.add_field(name="More Info", value=f"[Click Here](https://parcility.co/package/{self.data[self.index].get('Package')}/{self.data[self.index].get('repo').get('slug')})", inline=False)
        embed.set_thumbnail(url=self.data[self.index].get('Icon'))
        embed.set_footer(icon_url=self.data[self.index].get('repo').get('icon'), text=f"{self.data[self.index].get('repo').get('label')} • Page {self.index + 1}/{len(self.data)}")
        embed.timestamp = datetime.now()
        if message is None and channel is not None:
            return await channel.send(embed=embed)
        elif message is not None:
            return await message.edit(embed=embed)

    async def send_initial_message(self, ctx, channel):
        return await self.post_embed(channel=channel)
    
    @menus.button('\N{BLACK LEFT-POINTING TRIANGLE}\ufe0f')
    async def on_left_press(self, payload):
        if payload.event_type == "REACTION_ADD":
            if self.index == 0:
                await self.message.remove_reaction(emoji=payload.emoji, member=payload.member)
                return
            self.index -= 1
            await self.message.remove_reaction(emoji=payload.emoji, member=payload.member)
            await self.post_embed(message=self.message)

    @menus.button('\N{BLACK RIGHT-POINTING TRIANGLE}\ufe0f')
    async def on_right_press(self, payload):
        if payload.event_type == "REACTION_ADD":
            if (self.index + 1) >= len(self.data):
                await self.message.remove_reaction(emoji=payload.emoji, member=payload.member)
                return
            self.index += 1
            await self.message.remove_reaction(emoji=payload.emoji, member=payload.member)
            await self.post_embed(message=self.message)


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
            embed = discord.Embed(title="Error", color=discord.Color.red())
            embed.description = "An error occurred while searching for that tweak."
            await message.delete(delay=5)
            await message.channel.send(embed=embed, delete_after=5)
            return
        elif len(response) == 0:
            embed = discord.Embed(title="Not Found", color=discord.Color.red())
            embed.description = f'Sorry, I couldn\'t find any tweaks with the name "{search_term}"'
            await message.delete(delay=5)
            await message.channel.send(embed=embed, delete_after=5)
            return
        
        menu = TweakMenu(response)
        ctx = await self.bot.get_context(message)
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
            embed.description = f'An error occurred while searching for the repo "{repo}"'
            await ctx.message.delete(delay=5)
            await ctx.send(embed=embed, delete_after=5)
            return
        elif len(data) == 0:
            print("len")
            embed = discord.Embed(title="Not Found", color=discord.Color.red())
            embed.description = f'Sorry, I couldn\'t find a repo by the name "{repo}"'
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
