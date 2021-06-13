import datetime
import pytz
import traceback
import typing
import humanize

import discord
import cogs.utils.permission_checks as permissions
import cogs.utils.context as context
from data.case import Case
from discord.ext import commands


class ModUtils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.guild_only()
    @permissions.mod_and_up()
    @commands.command(name="rundown", aliases=['rd'])
    async def rundown(self, ctx: context.Context, user: discord.Member) -> None:
        """Get information about a user (join/creation date, xp, etc.), defaults to command invoker.

        Example usage:
        --------------
        `!userinfo <@user/ID (optional)>`

        Parameters
        ----------
        user : discord.Member, optional
            User to get info about, by default the author of command, by default None
        """

        await ctx.message.reply(embed=await self.prepare_rundown_embed(ctx, user))

    @commands.guild_only()
    @permissions.admin_and_up()
    @commands.command(name="transferprofile")
    async def transferprofile(self,  ctx: context.Context, oldmember: typing.Union[int, discord.Member], newmember: discord.Member):
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

        if isinstance(oldmember, int):
            try:
                oldmember = await self.bot.fetch_user(oldmember)
            except discord.NotFound:
                raise commands.BadArgument(
                    f"Couldn't find user with ID {oldmember}")

        u, case_count = await ctx.settings.transfer_profile(oldmember.id, newmember.id)

        embed = discord.Embed(title="Transferred profile")
        embed.description = f"We transferred {oldmember.mention}'s profile to {newmember.mention}"
        embed.color = discord.Color.blurple()
        embed.add_field(name="Level", value=u.level)
        embed.add_field(name="XP", value=u.xp)
        embed.add_field(name="Warnpoints", value=f"{u.warn_points} points")
        embed.add_field(name="Cases", value=f"We transfered {case_count} cases")

        await ctx.message.reply(embed=embed)
        
        try:
            await newmember.send(f"{ctx.author} has transferred your profile from {oldmember}", embed=embed)
        except Exception:
            pass

    @commands.guild_only()
    @permissions.guild_owner_and_up()
    @commands.command(name="clem")
    async def clem(self, ctx: context.Context, user: discord.Member) -> None:
        """Sets user's XP and Level to 0, freezes XP, sets warn points to 599 (AARON ONLY)

        Example usage:
        --------------
        `!clem <@user/ID>`

        Parameters
        ----------
        user : discord.Member
            User to put on clem

        """

        if user.id == ctx.author.id:
            await ctx.message.add_reaction("🤔")
            raise commands.BadArgument("You can't call that on yourself.")
        if user.id == self.bot.user.id:
            await ctx.message.add_reaction("🤔")
            raise commands.BadArgument("You can't call that on me :(")

        results = await ctx.settings.user(user.id)
        results.is_clem = True
        results.is_xp_frozen = True
        results.warn_points = 599
        results.save()

        case = Case(
            _id=ctx.settings.guild().case_id,
            _type="CLEM",
            mod_id=ctx.author.id,
            mod_tag=str(ctx.author),
            punishment=str(-1),
            reason="No reason."
        )

        # increment DB's max case ID for next case
        await ctx.settings.inc_caseid()
        # add case to db
        await ctx.settings.add_case(user.id, case)

        await ctx.message.reply(f"{user.mention} was put on clem.", allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False))

    @commands.guild_only()
    @permissions.mod_and_up()
    @commands.command(name="musicban")
    async def musicban(self, ctx: context.Context, user: discord.Member) -> None:
        """Ban a user from using music commands (mod only)

        Example usage:
        --------------
        `!musicban <@user/ID>`

        Parameters
        ----------
        user : discord.Member
            User to ban from music
        """

        if user.id == self.bot.user.id:
            await ctx.message.add_reaction("🤔")
            raise commands.BadArgument("You can't call that on me :(")

        results = await ctx.settings.user(user.id)
        results.is_music_banned = True
        results.save()
        
        await ctx.send_success(f"Banned {user.mention} from music.", delete_after=5)

    @commands.guild_only()
    @permissions.mod_and_up()
    @commands.command(name="birthdayexclude")
    async def birthdayexclude(self, ctx: context.Context, user: discord.Member) -> None:
        """Remove a user's birthday (mod only)

        Example usage:
        --------------
        `!birthdayexclude <@user/ID>`

        Parameters
        ----------
        user : discord.Member
            User to ban from birthdays
        """

        if user.id == self.bot.user.id:
            await ctx.message.add_reaction("🤔")
            raise commands.BadArgument("You can't call that on me :(")

        results = await ctx.settings.user(user.id)
        results.birthday_excluded = True
        results.birthday = None
        results.save()

        birthday_role = ctx.guild.get_role(ctx.settings.guild().role_birthday)
        if birthday_role is None:
            return

        if birthday_role in user.roles:
            await user.remove_roles(birthday_role)

        await ctx.message.reply(f"{user.mention} was banned from birthdays.", allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False))

    @commands.guild_only()
    @permissions.mod_and_up()
    @commands.command(name="removebirthday")
    async def removebirthday(self, ctx: context.Context, user: discord.Member) -> None:
        """Remove a user's birthday (mod only)

        Example usage:
        --------------
        `!removebirthday <@user/ID>`

        Parameters
        ----------
        user : discord.Member
            User to remove birthday of
        """

        if user.id == self.bot.user.id:
            await ctx.message.add_reaction("🤔")
            raise commands.BadArgument("You can't call that on me :(")

        results = await ctx.settings.user(user.id)
        results.birthday = None
        results.save()

        try:
            ctx.settings.tasks.cancel_unbirthday(user.id)
        except Exception:
            pass

        birthday_role = ctx.guild.get_role(ctx.settings.guild().role_birthday)
        if birthday_role is None:
            return

        if birthday_role in user.roles:
            await user.remove_roles(birthday_role)

        await ctx.message.reply(f"{user.mention}'s birthday was removed.", allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False), delete_after=5)
        await ctx.message.delete(delay=5)

    @commands.guild_only()
    @permissions.mod_and_up()
    @commands.command(name="setbirthday")
    async def setbirthday(self, ctx: context.Context, user: discord.Member, month: int, date: int) -> None:
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

        if user.id == self.bot.user.id:
            await ctx.message.add_reaction("🤔")
            raise commands.BadArgument("You can't call that on me :(")

        try:
            datetime.datetime(year=2020, month=month, day=date, hour=12)
        except ValueError:
            raise commands.BadArgument("You gave an invalid date.")

        results = await ctx.settings.user(user.id)
        results.birthday = [month, date]
        results.save()

        await ctx.message.reply(f"{user.mention}'s birthday was set.", allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False), delete_after=5)
        await ctx.message.delete(delay=5)

        if results.birthday_excluded:
            return

        eastern = pytz.timezone('US/Eastern')
        today = datetime.datetime.today().astimezone(eastern)
        if today.month == month and today.day == date:
            birthday_role = ctx.guild.get_role(ctx.settings.guild().role_birthday)
            if birthday_role is None:
                return
            print("here")
            if birthday_role in user.roles:
                return
            print("here2")
            now = datetime.datetime.now(eastern)
            h = now.hour / 24
            m = now.minute / 60 / 24

            try:
                time = now + datetime.timedelta(days=1-h-m)
                ctx.settings.tasks.schedule_remove_bday(user.id, time)
            except Exception as e:
                print(e)
                return
            await user.add_roles(birthday_role)
            await user.send(f"According to my calculations, today is your birthday! We've given you the {birthday_role} role for 24 hours.")

    async def prepare_rundown_embed(self,  ctx: context.Context, user):
        user_info = await ctx.settings.user(user.id)
        joined = user.joined_at.strftime("%B %d, %Y, %I:%M %p")
        created = user.created_at.strftime("%B %d, %Y, %I:%M %p")
        rd = await ctx.settings.rundown(user.id)
        rd_text = ""
        for r in rd:
            if r._type == "WARN":
                r.punishment += " points"
            rd_text += f"**{r._type}** - {r.punishment} - {r.reason} - {humanize.naturaltime(datetime.datetime.now() - r.date)}\n"

        reversed_roles = user.roles
        reversed_roles.reverse()

        roles = ""
        for role in reversed_roles[0:4]:
            if role != user.guild.default_role:
                roles += role.mention + " "
        roles = roles.strip() + "..."

        embed = discord.Embed(title="Rundown")
        embed.color = user.top_role.color
        embed.set_thumbnail(url=user.avatar_url)

        embed.add_field(name="Member", value=f"{user} ({user.mention}, {user.id})")
        embed.add_field(name="Join date", value=f"{joined} UTC")
        embed.add_field(name="Account creation date",
                        value=f"{created} UTC")
        embed.add_field(name="Warn points",
                        value=user_info.warn_points, inline=True)

        if user_info.is_clem:
            embed.add_field(
                name="XP", value="*this user is clemmed*", inline=True)
        else:
            embed.add_field(
                name="XP", value=f"{user_info.xp} XP", inline=True)
            embed.add_field(
                name="Level", value=f"Level {user_info.level}", inline=True)

        embed.add_field(
            name="Roles", value=roles if roles else "None", inline=False)

        if len(rd) > 0:
            embed.add_field(name=f"{len(rd)} most recent cases",
                            value=rd_text, inline=False)
        else:
            embed.add_field(name=f"Recent cases",
                            value="This user has no cases.", inline=False)
        embed.set_footer(text=f"Requested by {ctx.author}")

        return embed

    @musicban.error
    @birthdayexclude.error
    @removebirthday.error
    @setbirthday.error
    @transferprofile.error
    @rundown.error
    @clem.error
    async def info_error(self, ctx: context.Context,error):
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
    bot.add_cog(ModUtils(bot))
