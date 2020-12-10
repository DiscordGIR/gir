import logging
import os

import discord
from discord.ext import commands
from dotenv import find_dotenv, load_dotenv

logging.basicConfig(level=logging.INFO)

load_dotenv(find_dotenv())


def get_prefix(bot, message):
    """A callable Prefix for our bot. This could be edited to allow per server prefixes."""

    prefixes = ['!']

    # If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(bot, message)


initial_extensions = ['cogs.utils.settings',
                      'cogs.commands.mod.modactions',
                      'cogs.commands.mod.filter',
                      'cogs.commands.info.userinfo',
                      'cogs.commands.info.stats',
                      'cogs.commands.info.devices',
                      ]

monitor_extensions = [
                'cogs.monitors.logging',
                'cogs.monitors.filter',
                'cogs.monitors.xp',
]

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.presences = True
mentions = discord.AllowedMentions(everyone=False, users=True, roles=False)

bot = commands.Bot(command_prefix=get_prefix,
                   intents=intents, allowed_mentions=mentions)
bot.max_messages = 10000

# Here we load our extensions(cogs) listed above in [initial_extensions].
if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)


class NewHelpCommand(commands.DefaultHelpCommand):
    def __init__(self):
        super().__init__()
        self.dm_help = True

    async def prepare_help_command(self, ctx, command=None):
        await ctx.message.add_reaction("📬")
        await ctx.message.delete(delay=5)
        await super().prepare_help_command(ctx, command)

    async def command_not_found(self, ctx):
        return "Command not found!"

    async def subcommand_not_found(self, ctx, xd):
        return "Command not found!"


async def send_error(ctx, error):
    embed = discord.Embed(title="Your command ran into a problem :(")
    embed.color = discord.Color.red()
    embed.description = discord.utils.escape_markdown(f'{error}')
    await ctx.send(embed=embed, delete_after=8)


@bot.event
async def on_ready():
    bot.help_command = NewHelpCommand()
    bot.settings = bot.get_cog("Settings")
    bot.send_error = send_error
    bot.owner_id = int(os.environ.get("BOTTY_OWNER"))

    await bot.wait_until_ready()

    for extension in monitor_extensions:
        bot.load_extension(extension)

    print(
        f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')
    await bot.settings.load_tasks()
    print(f'Successfully logged in and booted...!')


bot.run(os.environ.get("BOTTY_TOKEN"), bot=True, reconnect=True)
