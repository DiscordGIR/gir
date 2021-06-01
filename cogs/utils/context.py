from datetime import datetime, timedelta
import discord 
import asyncio
from discord.ext import commands
import pytimeparse

class Context(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = self.bot.settings
        self.permissions = self.bot.settings.permissions
        self.tasks = self.bot.settings.tasks
        
    async def send_success(self, description: str, delete_after: int = None):
        return await self.reply(embed=discord.Embed(description=description, color=discord.Color.blurple()), delete_after=delete_after)
    
    async def prompt(self, value, data):
        """Custom prompt system

           Data format is a dictionary:
           {
               'prompt': "The message to ask the user",
               'converter': function to use as converter, for example str or commands.MemberConverter().convert,
               'event': optional, if you want to prompt for reaction for example
           }
        """
        
        question = data['prompt']
        convertor = data['convertor']
        event = data.get('event') or 'message'

        def wait_check(m):
            return m.author == self.author and m.channel == self.channel
    
        ret = None
        prompt = await self.send(embed=discord.Embed(description=question, color=discord.Color.blurple()))
        try:
            response = await self.bot.wait_for(event, check=wait_check, timeout=120)
        except asyncio.TimeoutError:
            await prompt.delete()
            return
        else:
            await response.delete()
            await prompt.delete()
            if response.content.lower() == "cancel":
                return
            elif response.content is not None and response.content != "":
                if convertor in [str, int, pytimeparse.parse]:
                    try:
                        ret = convertor(response.content)
                    except Exception:
                        ret = None
                    
                    if ret is None:
                        raise commands.BadArgument(f"Could not parse value for parameter \"{value}\".")

                    if convertor is pytimeparse.parse:
                        now = datetime.now()
                        time = now + timedelta(seconds=ret)
                        if time < now:
                            raise commands.BadArgument("Time has to be in the future >:(")

                else:
                    ret = await convertor(self, response.content)
                    
        return ret

        
    async def send_error(self, error):
        embed = discord.Embed(title=":(\nYour command ran into a problem")
        embed.color = discord.Color.red()
        embed.description = discord.utils.escape_markdown(f'{error}')
        await self.send(embed=embed, delete_after=8)
