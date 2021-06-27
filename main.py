import logging
import os

import discord
from cogs.utils.filter import Filter
import cogs.utils.context as context
from discord.ext import commands
from dotenv import find_dotenv, load_dotenv

from cogs.monitors.report import Report

logging.basicConfig(level=logging.INFO)

load_dotenv(find_dotenv())


def get_prefix(bot, message):
    """A callable Prefix for our bot. This could be edited to allow per server prefixes."""

    prefixes = ['!']

    # If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(bot, message)


initial_extensions = [
                    'cogs.commands.mod.modactions',
                    'cogs.commands.mod.modutils',
                    'cogs.commands.mod.antiraid',
                    'cogs.commands.mod.trivia',
                    'cogs.commands.misc.admin',
                    'cogs.commands.misc.genius',
                    'cogs.commands.misc.misc',
                    'cogs.commands.misc.subnews',
                    'cogs.commands.misc.giveaway',
                    'cogs.commands.misc.parcility',
                    'cogs.commands.info.devices',
                    'cogs.commands.info.help',
                    'cogs.commands.info.stats',
                    'cogs.commands.info.tags',
                    'cogs.commands.info.userinfo',
                    'cogs.commands.mod.filter',
                    'cogs.monitors.antiraid',
                    'cogs.monitors.applenews',
                    'cogs.monitors.birthday',
                    'cogs.monitors.boosteremojis',
                    'cogs.monitors.filter',
                    'cogs.monitors.logging',
                    'cogs.monitors.reactionroles',
                    'cogs.monitors.xp',
]

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.presences = True
mentions = discord.AllowedMentions(everyone=False, users=True, roles=False)

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_extension('cogs.utils.settings')
        self.settings = self.get_cog("Settings")
        self.reports = Report(self)
        self.filters = Filter(self)
    
    async def on_message(self, message):
        if message.author.bot:
            return
        
        if message.guild is not None and message.guild.id == self.settings.guild_id:
            if not self.settings.permissions.hasAtLeast(message.guild, message.author, 6):
                role_submod = message.guild.get_role(self.settings.guild().role_sub_mod)
                if role_submod is not None:
                    if role_submod not in message.author.roles:
                        if await self.filters.filter(message):
                            return
                else:
                    if await self.filters.filter(message):
                        return
                                
        await self.process_commands(message)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=context.Context)
        await self.invoke(ctx)


bot = Bot(command_prefix=get_prefix,
                   intents=intents, allowed_mentions=mentions)
bot.max_messages = 10000

# Here we load our extensions(cogs) listed above in [initial_extensions].
if __name__ == '__main__':
    bot.owner_id = int(os.environ.get("BOTTY_OWNER"))
    bot.remove_command("help")
    for extension in initial_extensions:
        bot.load_extension(extension)


async def run_once_when_ready():
    await bot.wait_until_ready()

    print(
        f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')
    # bot.load_extension('cogs.commands.misc.music')
    await bot.settings.load_tasks()
    print(f'Successfully logged in and booted...!')


bot.loop.create_task(run_once_when_ready())
bot.run(os.environ.get("BOTTY_TOKEN"), bot=True, reconnect=True)
