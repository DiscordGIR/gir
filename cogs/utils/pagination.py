import discord


class PaginationSource:
    def __init__(self):
        


class PaginationView(discord.ui.View):
    def __init__(self, embeds_source):
        super().__init__()
        
        self.ctx = None
        self.embed_message = None

        self.emebds = embeds
        self.index = 0
        self.max_index = len(embeds) - 1
    
    
    async def start(self, ctx):
        self.ctx = ctx
        self.embed_message = await ctx.send(embed=self.embeds[0], view=self)

    @discord.ui.button(emoji="➡️", style=discord.ButtonStyle.secondary)
    async def _next(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user == self.ctx.author and self.index + 1 <= self.max_index:
            self.index += 1
            await self.update_embed(interaction)


    @discord.ui.button(emoji="⬅️", style=discord.ButtonStyle.secondary)
    async def _previous(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user == self.ctx.author and self.index > 0:
            self.index -= 1
            await self.update_embed(interaction)
            
    async def update_embed(self, interaction):
        await interaction.response.edit_message(embed=self.embeds[self.index], view=self)


