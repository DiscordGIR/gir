import traceback
from datetime import datetime, timedelta

import cogs.utils.context as context
import cogs.utils.permission_checks as permissions
import discord
import pytz
from discord.ext import commands, tasks


class Birthday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.birthday.start()
        self.eastern_timezone = pytz.timezone('US/Eastern')


    def cog_unload(self):
        self.birthday.cancel()

    @tasks.loop(seconds=120)
    async def birthday(self):
        """Background task to scan database for users whose birthday it is today.
        If it's someone's birthday, the bot will assign them the birthday role for 24 hours."""
        
        # assign the role at 12am US Eastern time
        eastern = pytz.timezone('US/Eastern')
        today = datetime.today().astimezone(eastern)
        # the date we will check for in the database
        date = [today.month, today.day]
        # get list of users whose birthday it is today
        birthdays = await self.bot.settings.retrieve_birthdays(date)
        
        guild = self.bot.get_guild(self.bot.settings.guild_id)
        if not guild:
            return
        
        birthday_role = guild.get_role(self.bot.settings.guild().role_birthday)
        if not birthday_role:
            return
        
        # give each user whose birthday it is today the birthday role
        for person in birthdays:
            if person.birthday_excluded:
                continue
            
            user = guild.get_member(person._id)
            if user is None:
                return
            
            await self.give_user_birthday_role(user, guild)
            
    @commands.guild_only()
    @permissions.bot_channel_only_unless_mod()
    @commands.command(name="mybirthday")
    async def mybirthday(self, ctx: context.Context, month: int, date: int) -> None:
        """Set your birthday. The birthday role will be given to you on that day. THIS COMMAND IS ONE TIME USE ONLY!

        Example usage
        --------------
        !mybirthday 7 18

        Parameters
        ----------
        month : int
            "Month of birthday"
        date : int
            "Date of birthday"
        """

        user = ctx.author

        if not (ctx.permissions.hasAtLeast(ctx.guild, ctx.author, 1) or user.premium_since is not None):
            raise commands.BadArgument(
                "You need to be at least Member+ or a Nitro booster to use that command.")
        
        # ensure date is real (2020 is a leap year in case the birthday is leap day)
        try:
            datetime(year=2020, month=month, day=date, hour=12)
        except ValueError:
            raise commands.BadArgument("You gave an invalid date.")

        # fetch user profile from DB
        results = await ctx.settings.user(user.id)

        # mods are able to ban users from using birthdays, let's handle that
        if results.birthday_excluded:
            raise commands.BadArgument("You are banned from birthdays.")

        # if the user already has a birthday set in the database, refuse to change it (if not a mod)
        if results.birthday != [] and not ctx.permissions.hasAtLeast(ctx.guild, ctx.author, 5):
            raise commands.BadArgument(
                "You already have a birthday set! You need to ask a mod to change it.")

        # passed all the sanity checks, let's save the birthday
        results.birthday = [month, date]
        results.save()

        await ctx.message.reply(f"{user.mention}'s birthday was set.", allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False), delete_after=5)
        await ctx.message.delete(delay=5)
        # if it's the user's birthday today let's assign the role right now!
        today = datetime.today().astimezone(self.eastern_timezone)
        if today.month == month and today.day == date:
            await self.give_user_birthday_role(ctx.author, ctx.guild)
        
    async def give_user_birthday_role(self, user, guild):
        birthday_role = guild.get_role(self.bot.settings.guild().role_birthday)
        if birthday_role is None:
            return

        if birthday_role in user.roles:
            return
        
        # calculate the different between now and tomorrow 12AM
        now = datetime.now(self.eastern_timezone)
        h = now.hour / 24
        m = now.minute / 60 / 24
        
        # schedule a task to remove birthday role (tomorrow) 12AM
        try:
            time = now + timedelta(days=1-h-m)
            self.bot.settings.tasks.schedule_remove_bday(user.id, time)
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
