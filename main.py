import discord
from discord.ext import commands
import os
from dotenv import load_dotenv, find_dotenv
import data.mongo_setup as mongo_setup
from data.case import Case
from data.scheduler import Scheduler
load_dotenv(find_dotenv())

def get_prefix(bot, message):
    """A callable Prefix for our bot. This could be edited to allow per server prefixes."""

    prefixes = ['!']

    # If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(bot, message)



initial_extensions = ['cogs.utils.settings',
                    'cogs.commands.mod.cases', 
                    'cogs.commands.mod.modactions', 
                    'cogs.commands.info.userinfo',
                    'cogs.commands.info.serverinfo',
                    'cogs.monitors.logging',]

intents = discord.Intents.default()
intents.members = True
intents.messages = True

bot = commands.Bot(command_prefix=get_prefix, intents=intents)
bot.max_messages = 1000000


# Here we load our extensions(cogs) listed above in [initial_extensions].
if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)


@bot.event
async def on_ready():
    bot.owner_id = os.environ.get("BOTTY_OWNER")
    bot.settings = bot.get_cog("Settings")
    bot.scheduler = Scheduler(bot)
    await bot.wait_until_ready()
    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')

    # cases = await bot.settings.cases(109705860275539968)
    # case = Case()
    # case._id = 1
    # case._type = "KICK"
    # case.mod_id = 123
    # case.mod_tag = "Slim#99"
    # case.reason = "xd"
    # case.punishment = "xd"
    # cases.cases.append(case)
    # cases.save()
    # Changes our bots Playing Status. type=1(streaming) for a standard game you could remove type and url.
    print(f'Successfully logged in and booted...!')


bot.run(os.environ.get("BOTTY_TOKEN"), bot=True, reconnect=True)