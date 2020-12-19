import discord
from datetime import datetime, timedelta
from discord.ext import tasks, commands

class Birthday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.birthday.start()

    def cog_unload(self):
        self.birthday.cancel()

    @tasks.loop(seconds=900)
    async def birthday(self):
        today = datetime.today()
        date = [today.month, today.day]
        birthdays = await self.bot.settings.retrieve_birthdays(date)
        guild = self.bot.get_guild(self.bot.settings.guild_id)

        if not guild:
            return
        birthday_role = guild.get_role(self.bot.settings.guild().role_birthday)
        if not birthday_role:
            return
        for person in birthdays:
            user = guild.get_member(person._id)
            if birthday_role in user.roles:
                continue
            try:
                time = datetime.now() + timedelta(days=1)
                self.bot.settings.tasks.schedule_remove_bday(user.id, time)
            except Exception:
                continue
            await user.add_roles(birthday_role)
            await user.send(f"According to my calculations, today is your birthday! We've given you the {birthday_role} role for 24 hours.")


def setup(bot):
    bot.add_cog(Birthday(bot))
