import discord
from discord.ext import commands

def get_prefix(bot, message):
    """A callable Prefix for our bot. This could be edited to allow per server prefixes."""

    prefixes = ['!']

    # If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(bot, message)



initial_extensions = ['cogs.utils.settings', 'cogs.commands.mod.cases']

bot = commands.Bot(command_prefix=get_prefix, description='A Rewrite Cog Example')

# Here we load our extensions(cogs) listed above in [initial_extensions].
if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)


@bot.event
async def on_ready():
    bot.owner_id = 109705860275539968
    bot.settings = bot.get_cog("Settings")
    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')

    # Changes our bots Playing Status. type=1(streaming) for a standard game you could remove type and url.
    print(f'Successfully logged in and booted...!')


bot.run('Nzc3MjgyNDQ0OTMxMTA0NzY5.X7BKsA.SZwCCsEafGdZDzhV6DY4nrdRErA', bot=True, reconnect=True)