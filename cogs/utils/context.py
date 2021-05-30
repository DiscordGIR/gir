import discord 
from discord.ext import commands

class Context(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = self.bot.settings
        self.permissions = self.bot.settings.permissions
        self.tasks = self.bot.settings.tasks
        
    # TODO: send_success
    # TODO: prompt
        
    async def send_error(self, ctx: context.Context,error):
        embed = discord.Embed(title=":(\nYour command ran into a problem")
        embed.color = discord.Color.red()
        embed.description = discord.utils.escape_markdown(f'{error}')
        await ctx.send(embed=embed, delete_after=8)
