from datetime import datetime, timedelta
import discord 
import asyncio
from discord.ext import commands
import pytimeparse

class PromptData:
    def __init__(self, value_name, description, convertor, timeout=120, title="", reprompt=False):
        self.value_name = value_name
        self.description = description
        self.convertor = convertor
        self.title = title
        self.reprompt = reprompt
        self.timeout = timeout
        
    def __copy__(self):
        return PromptData(self.value_name, self.description, self.convertor, self.title, self.reprompt)


class PromptDataReaction:
    def __init__(self, message, reactions, timeout=None, delete_after=False, raw_emoji=False):
        self.message = message
        self.reactions = reactions        
        self.timeout = timeout
        self.delete_after = delete_after
        self.raw_emoji = raw_emoji


class Context(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = self.bot.settings
        self.permissions = self.bot.settings.permissions
        self.tasks = self.bot.settings.tasks
    
    async def prompt(self, info: PromptData):
        def wait_check(m):
            return m.author == self.author and m.channel == self.channel
    
        ret = None
        embed = discord.Embed(
            title=info.title if not info.reprompt else f"That wasn't a valid {info.value_name}. {info.title if info.title is not None else ''}",
            description=info.description,
            color=discord.Color.blurple() if not info.reprompt else discord.Color.orange())
        embed.set_footer(text="Send 'cancel' to cancel.")
        
        prompt_msg = await self.send(embed=embed)
        try:
            response = await self.bot.wait_for('message', check=wait_check, timeout=info.timeout)
        except asyncio.TimeoutError:
            await prompt_msg.delete()
            return
        else:
            await response.delete()
            await prompt_msg.delete()
            if response.content.lower() == "cancel":
                return
            elif not response.content:
                info.reprompt = True
                return await self.prompt(info)
            else:
                if info.convertor in [str, int, pytimeparse.parse]:
                    try:
                        ret = info.convertor(response.content)
                    except Exception:
                        ret = None
                    
                    if ret is None:
                        info.reprompt = True
                        return await self.prompt(info)

                    if info.convertor is pytimeparse.parse:
                        now = datetime.now()
                        time = now + timedelta(seconds=ret)
                        if time < now:
                            raise commands.BadArgument("Time has to be in the future >:(")

                else:
                    ret = await info.convertor(self, response.content)
                    
        return ret
    
    async def prompt_reaction(self, info: PromptDataReaction):
        for reaction in info.reactions:
            await info.message.add_reaction(reaction)
            
        def wait_check(reaction, user):
            res = (user.id != self.bot.user.id
                and reaction.message == info.message)
            
            if info.reactions:
                res = res and str(reaction.emoji) in info.reactions
            
            return res
            
        if info.timeout is None:
            while True:
                try:
                    reaction, reactor = await self.bot.wait_for('reaction_add', timeout=300.0, check=wait_check)
                    if reaction is not None:
                        return str(reaction.emoji), reactor    
                except asyncio.TimeoutError:
                    if self.bot.report.pending_tasks.get(info.message.id) == "TERMINATE":
                        return "TERMINATE", None
        else:
            try:
                reaction, reactor = await self.bot.wait_for('reaction_add', timeout=info.timeout, check=wait_check)
            except asyncio.TimeoutError:
                try:
                    if info.delete_after:
                        await info.message.delete()
                    else:
                        await info.message.clear_reactions()
                    return None, None
                except Exception:
                    pass
            else:
                if info.delete_after:
                    await info.message.delete()
                else:
                    await info.message.clear_reactions()
                
                if not info.raw_emoji:
                    return str(reaction.emoji), reactor    
                else:
                    return reaction, reactor    
        
    async def send_warning(self, description: str, title="", delete_after: int = None):
        return await self.reply(embed=discord.Embed(title=title, description=description, color=discord.Color.orange()), delete_after=delete_after)

    async def send_success(self, description: str, title="", delete_after: int = None):
        return await self.reply(embed=discord.Embed(title=title, description=description, color=discord.Color.dark_green()), delete_after=delete_after)
        
    async def send_error(self, error):
        embed = discord.Embed(title=":(\nYour command ran into a problem")
        embed.color = discord.Color.red()
        embed.description = str(error)
        await self.send(embed=embed, delete_after=8)
