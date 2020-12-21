import discord
from datetime import datetime, timedelta
import traceback
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
            if person.birthday_excluded:
                continue
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

    @commands.guild_only()
    @commands.command(name="mybirthday")
    async def mybirthday(self, ctx: commands.Context, month: int, date: int) -> None:
        """Set your birthday. The birthday role will be given to you on the given day.

        Example usage:
        --------------
        `!mybirthday <month (int)> <date (int)>`

        Parameters
        ----------
        month : int
            Month of birthday
        date : int
            Date of birthday
        """

        user = ctx.author

        bot_chan = self.bot.settings.guild().channel_botspam
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 5) and ctx.channel.id != bot_chan:
            raise commands.BadArgument(
                f"Command only allowed in <#{bot_chan}>")

        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 1):
            raise commands.BadArgument(
                "You need to be at least Member+ to use that command.")
        try:
            datetime(year=2020, month=month, day=date, hour=12)
        except ValueError:
            raise commands.BadArgument("You gave an invalid date.")

        results = await self.bot.settings.user(user.id)

        if results.birthday_excluded:
            raise commands.BadArgument("You are banned from birthdays.")

        if results.birthday != [] and not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 5):
            raise commands.BadArgument(
                "You already have a birthday set! You need to ask a mod to change it.")

        results.birthday = [month, date]
        results.save()
        
        await ctx.message.reply(f"{user.mention}'s birthday was set.", allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False))
        
        today = datetime.today()
        if today.month == month and today.day == date:
            birthday_role = ctx.guild.get_role(self.bot.settings.guild().role_birthday)
            if birthday_role is None:
                return
            
            if birthday_role in user.roles:
                return
            
            try:
                time = datetime.now() + timedelta(days=1)
                self.bot.settings.tasks.schedule_remove_bday(user.id, time)
            except Exception:
                return
            await user.add_roles(birthday_role)
            await user.send(f"According to my calculations, today is your birthday! We've given you the {birthday_role} role for 24 hours.")




    @mybirthday.error
    async def info_error(self, ctx, error):
        await ctx.message.delete(delay=5)
        if (isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.BotMissingPermissions)
            or isinstance(error, commands.MissingPermissions)
                or isinstance(error, commands.NoPrivateMessage)):
            await self.bot.send_error(ctx, error)
        else:
            await self.bot.send_error(ctx, error)
            traceback.print_exc()


def setup(bot):
    bot.add_cog(Birthday(bot))
