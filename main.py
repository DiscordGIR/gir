import discord
import os
from discord.ext import commands
from dotenv.main import load_dotenv
from utils.config import cfg
from utils.logger import logger
from model.guild import Guild


initial_extensions = ["cog"]

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.guild_id = cfg.guild_id

bot = Bot()

@bot.event
async def on_ready():
    logger.info(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')
    logger.info(f'Successfully logged in and booted...!')


if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

bot.run(os.environ.get("GIR_TOKEN"), reconnect=True)