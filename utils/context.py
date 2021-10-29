from discord.utils import MISSING
from discord.colour import Color
from discord.commands import context
from discord.embeds import Embed

class GIRContext(context.ApplicationContext):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.whisper = False


    async def respond_or_edit(self, *args, **kwargs):
        if self.interaction.response.is_done():
            del kwargs["ephemeral"]
            await self.edit(*args, **kwargs)
        else:
            await self.respond(*args, **kwargs)

    async def send_success(self, description: str, title: str = ""):
        embed = Embed(title=title, description=description,  color=Color.dark_green())
        await self.respond_or_edit(content="", embed=embed, ephemeral=self.whisper, view=MISSING)
    
    async def send_warning(self, description: str, title: str = ""):
        embed = Embed(title=title, description=description,  color=Color.orange())
        await self.respond_or_edit(content="", embed=embed, ephemeral=self.whisper, view=MISSING)
    
    async def send_error(self, description):
        embed = Embed(title=":(\nYour command ran into a problem", description=description,  color=Color.orange())
        await self.respond_or_edit(content="", embed=embed, ephemeral=self.whisper, view=MISSING)