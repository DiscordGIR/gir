import discord
from discord.ext import tasks, commands

class Birthday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.birthday.start()

    def cog_unload(self):
        self.birthday.cancel()

    @tasks.loop(seconds=3600)
    async def birthday(self):
        now = datetime.datetime.today()
        date = [today.month, today.day]
        birthdays = await self.bot.settings.retrieve_birthdays(date)
        guild = self.bot.settings.get_guild(self.bot.settings.guild_id)

        if guild:
            for person in birthdays:
                user = guild.get_user(person._id)
                # birthday_role = 

