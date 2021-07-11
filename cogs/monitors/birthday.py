import discord
from datetime import datetime, timedelta
import pytz
import traceback
import cogs.utils.permission_checks as permissions
import cogs.utils.context as context
from discord.ext import tasks, commands

class Birthday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.birthday.start()

    def cog_unload(self):
        self.birthday.cancel()

    @tasks.loop(seconds=900)
    async def birthday(self):
        eastern = pytz.timezone('US/Eastern')
        today = datetime.today().astimezone(eastern)
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
            if user is None:
                return
            if birthday_role in user.roles:
                continue
            
            now = datetime.now(eastern)
            h = now.hour / 24
            m = now.minute / 60 / 24

            try:
                time = now + timedelta(days=1-h-m)
                self.bot.settings.tasks.schedule_remove_bday(user.id, time)
            except Exception as e:
                continue
            await user.add_roles(birthday_role)
            try:
                await user.send(f"According to my calculations, today is your birthday! We've given you the {birthday_role} role for 36 hours.")
            except Exception:
                pass
            
    @commands.guild_only()
    @permissions.bot_channel_only_unless_mod()
    @commands.command(name="mybirthday")
    async def mybirthday(self, ctx: context.Context, month: int, date: int) -> None:
        """Set your birthday. The birthday role will be given to you on that day. THIS COMMAND IS ONE TIME USE ONLY!

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

        if not (ctx.permissions.hasAtLeast(ctx.guild, ctx.author, 1) or user.premium_since is not None):
            raise commands.BadArgument(
                "You need to be at least Member+ or a Nitro booster to use that command.")
        try:
            datetime(year=2020, month=month, day=date, hour=12)
        except ValueError:
            raise commands.BadArgument("You gave an invalid date.")

        results = await ctx.settings.user(user.id)

        if results.birthday_excluded:
            raise commands.BadArgument("You are banned from birthdays.")

        if results.birthday != [] and not ctx.permissions.hasAtLeast(ctx.guild, ctx.author, 5):
            raise commands.BadArgument(
                "You already have a birthday set! You need to ask a mod to change it.")

        results.birthday = [month, date]
        results.save()

        await ctx.message.reply(f"{user.mention}'s birthday was set.", allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False), delete_after=5)
        await ctx.message.delete(delay=5)

        eastern = pytz.timezone('US/Eastern')
        today = datetime.today().astimezone(eastern)
        if today.month == month and today.day == date:
            birthday_role = ctx.guild.get_role(ctx.settings.guild().role_birthday)
            if birthday_role is None:
                return

            if birthday_role in user.roles:
                return
            
            now = datetime.now(eastern)
            h = now.hour / 24
            m = now.minute / 60 / 24

            try:
                time = now + timedelta(days=1-h-m)
                ctx.tasks.schedule_remove_bday(user.id, time)
            except Exception:
                return
            await user.add_roles(birthday_role)
            try:
                await user.send(f"According to my calculations, today is your birthday! We've given you the {birthday_role} role for 24 hours.")
            except Exception:
                pass
            
    @mybirthday.error
    async def info_error(self,  ctx: context.Context, error):
        await ctx.message.delete(delay=5)
        if (isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, permissions.PermissionsFailure)
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.BotMissingPermissions)
            or isinstance(error, commands.MissingPermissions)
                or isinstance(error, commands.NoPrivateMessage)):
            await ctx.send_error(error)
        else:
            await ctx.send_error(error)
            traceback.print_exc()


def setup(bot):
    bot.add_cog(Birthday(bot))
