import datetime
import traceback
import typing

import discord
from data.case import Case
from discord.ext import commands


class ModUtils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def check_permissions(self, ctx, user: typing.Union[discord.Member, int] = None):
        if isinstance(user, discord.Member):
            if user.id == ctx.author.id:
                await ctx.message.add_reaction("🤔")
                raise commands.BadArgument("You can't call that on yourself.")
            if user.id == self.bot.user.id:
                await ctx.message.add_reaction("🤔")
                raise commands.BadArgument("You can't call that on me :(")

        # must be at least a mod
            raise commands.BadArgument(
                "You do not have permission to use this command.")
        if user:
            if isinstance(user, discord.Member):
                if user.top_role >= ctx.author.top_role:
                    raise commands.BadArgument(
                        message=f"{user.mention}'s top role is the same or higher than yours!")

    @commands.guild_only()
    @commands.command(name="transferprofile")
    async def transferprofile(self, ctx, oldmember: typing.Union[int, discord.Member], newmember: discord.Member):
        """Transfer all data in the database between users (admin only)

        Example usage
        -------------
        !transferprofile <@olduser/ID> <@newuser/ID>

        Parameters
        ----------
        oldmember : typing.Union[int, discord.Member]
            ID/@tag of the old user, optionally in the guild
        newmember : discord.Member
            ID/@tag of the new user, must be in the

        """

        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 6):
            raise commands.BadArgument(
                "You need to be at least an Administrator to use that command.")

        if isinstance(oldmember, int):
            try:
                oldmember = await self.bot.fetch_user(oldmember)
            except discord.NotFound:
                raise commands.BadArgument(
                    f"Couldn't find user with ID {oldmember}")

        u, case_count = await self.bot.settings.transfer_profile(oldmember.id, newmember.id)

        embed = discord.Embed(title="Transferred profile")
        embed.description = f"We transferred {oldmember.mention}'s profile to {newmember.mention}'"
        embed.add_field(name="Level", value=u.level)
        embed.add_field(name="XP", value=u.xp)
        embed.add_field(name="Warnpoints", value=f"{u.warn_points} points")
        embed.add_field(name="Cases", value=f"We transfered {case_count} cases")

        await ctx.message.reply(embed=embed, delete_after=10)
        await ctx.message.delete(delay=10)

    @commands.guild_only()
    @commands.command(name="clem")
    async def clem(self, ctx: commands.Context, user: discord.Member) -> None:
        """Sets user's XP and Level to 0, freezes XP, sets warn points to 599 (AARON ONLY)

        Example usage:
        --------------
        `!clem <@user/ID>`

        Parameters
        ----------
        user : discord.Member
            User to put on clem

        """

        # must be owner
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 7):
            raise commands.BadArgument(
                "You need to be Aaron to use that command.")
        if user.id == ctx.author.id:
            await ctx.message.add_reaction("🤔")
            raise commands.BadArgument("You can't call that on yourself.")
        if user.id == self.bot.user.id:
            await ctx.message.add_reaction("🤔")
            raise commands.BadArgument("You can't call that on me :(")

        results = await self.bot.settings.user(user.id)
        results.is_clem = True
        results.is_xp_frozen = True
        results.warn_points = 599
        results.save()

        case = Case(
            _id=self.bot.settings.guild().case_id,
            _type="CLEM",
            mod_id=ctx.author.id,
            mod_tag=str(ctx.author),
            punishment=str(-1),
            reason="No reason."
        )

        # increment DB's max case ID for next case
        await self.bot.settings.inc_caseid()
        # add case to db
        await self.bot.settings.add_case(user.id, case)

        await ctx.message.reply(f"{user.mention} was put on clem.", allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False))

    @commands.guild_only()
    @commands.command(name="birthdayexclude")
    async def birthdayexclude(self, ctx: commands.Context, user: discord.Member) -> None:
        """Remove a user's birthday (mod only)

        Example usage:
        --------------
        `!birthdayexclude <@user/ID>`

        Parameters
        ----------
        user : discord.Member
            User to ban from birthdays
        """

        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 5):
            raise commands.BadArgument(
                "You need to be at least a Moderator to use that command.")

        if user.id == self.bot.user.id:
            await ctx.message.add_reaction("🤔")
            raise commands.BadArgument("You can't call that on me :(")

        results = await self.bot.settings.user(user.id)
        results.birthday_excluded = True
        results.birthday = None
        results.save()

        birthday_role = ctx.guild.get_role(self.bot.settings.guild().role_birthday)
        if birthday_role is None:
            return

        if birthday_role in user.roles:
            await user.remove_roles(birthday_role)

        await ctx.message.reply(f"{user.mention} was banned from birthdays.", allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False))

    @commands.guild_only()
    @commands.command(name="removebirthday")
    async def removebirthday(self, ctx: commands.Context, user: discord.Member) -> None:
        """Remove a user's birthday (mod only)

        Example usage:
        --------------
        `!removebirthday <@user/ID>`

        Parameters
        ----------
        user : discord.Member
            User to remove birthday of
        """

        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 5):
            raise commands.BadArgument(
                "You need to be at least a Moderator to use that command.")

        if user.id == self.bot.user.id:
            await ctx.message.add_reaction("🤔")
            raise commands.BadArgument("You can't call that on me :(")

        results = await self.bot.settings.user(user.id)
        results.birthday = None
        results.save()

        birthday_role = ctx.guild.get_role(self.bot.settings.guild().role_birthday)
        if birthday_role is None:
            return

        if birthday_role in user.roles:
            await user.remove_roles(birthday_role)

        await ctx.message.reply(f"{user.mention}'s birthday was removed.", allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False), delete_after=5)
        await ctx.message.delete(delay=5)

    @commands.guild_only()
    @commands.command(name="setbirthday")
    async def setbirthday(self, ctx: commands.Context, user: discord.Member, month: int, date: int) -> None:
        """Override a user's birthday (mod only)

        Example usage:
        --------------
        `!setbirthday <@user/ID> <month (int)> <date (int)>`

        Parameters
        ----------
        user : discord.Member
            User whose bithday to set
        month : int
            Month of birthday
        date : int
            Date of birthday
        """

        # must be mod
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 5):
            raise commands.BadArgument(
                "You need to be at least a Moderator to use that command.")

        if user.id == self.bot.user.id:
            await ctx.message.add_reaction("🤔")
            raise commands.BadArgument("You can't call that on me :(")

        try:
            datetime.datetime(year=2020, month=month, day=date, hour=12)
        except ValueError:
            raise commands.BadArgument("You gave an invalid date.")

        results = await self.bot.settings.user(user.id)
        results.birthday = [month, date]
        results.save()

        await ctx.message.reply(f"{user.mention}'s birthday was set.", allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False), delete_after=5)
        await ctx.message.delete(delay=5)

        if results.birthday_excluded:
            return

        today = datetime.datetime.today()
        if today.month == month and today.day == date:
            birthday_role = ctx.guild.get_role(self.bot.settings.guild().role_birthday)
            if birthday_role is None:
                return

            if birthday_role in user.roles:
                return

            try:
                time = datetime.datetime.now() + datetime.timedelta(days=1)
                self.bot.settings.tasks.schedule_remove_bday(user.id, time)
            except Exception as e:
                print(e)
                return
            await user.add_roles(birthday_role)
            await user.send(f"According to my calculations, today is your birthday! We've given you the {birthday_role} role for 24 hours.")

    @birthdayexclude.error
    @removebirthday.error
    @setbirthday.error
    @transferprofile.error
    @clem.error
    async def info_error(self, ctx, error):
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
    bot.add_cog(ModUtils(bot))
