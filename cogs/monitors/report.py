import asyncio
import datetime

import discord
import humanize
from data.case import Case
from cogs.utils import logs as logging


async def report(bot, msg, user, invite = None):
    role = msg.guild.get_role(bot.settings.guild().role_moderator)
    channel = msg.guild.get_channel(bot.settings.guild().channel_reports)

    ping_string = ""
    for member in role.members:
        offline_ping = (await bot.settings.user(member.id)).offline_report_ping
        if member.status == discord.Status.online or offline_ping:
            ping_string += f"{member.mention} "

    user_info = await bot.settings.user(user.id)
    joined = user.joined_at.strftime("%B %d, %Y, %I:%M %p")
    created = user.created_at.strftime("%B %d, %Y, %I:%M %p")
    rd = await bot.settings.rundown(user.id)
    rd_text = ""
    for r in rd:
        if r._type == "WARN":
            r.punishment += " points"
        rd_text += f"**{r._type}** - {r.punishment} - {r.reason} - {humanize.naturaltime(datetime.datetime.now() - r.date)}\n"

    embed = discord.Embed(title="Word filter")
    embed.color = discord.Color.red()
    # embed.description = ":warning:: Warn for 50 points\n:100:: Warn for 100 points"
    embed.set_thumbnail(url=user.avatar_url)
    embed.add_field(name="Member", value=f"{user} ({user.mention})")
    embed.add_field(name="Channel", value=msg.channel.mention)

    if len(msg.content) > 400:
        msg.content = msg.content[0:400] + "..."

    embed.add_field(name="Message", value=discord.utils.escape_markdown(
        msg.content) + f"\n\n[Link to message]({msg.jump_url})", inline=False)
    embed.add_field(name="Join date", value=f"{joined} UTC", inline=True)
    embed.add_field(name="Account creation date",
                    value=f"{created} UTC", inline=True)
    embed.add_field(name="Warn points",
                    value=user_info.warn_points, inline=True)
    if len(rd) > 0:
        embed.add_field(name=f"{len(rd)} most recent cases",
                        value=rd_text, inline=True)
    else:
        embed.add_field(name=f"Recent cases",
                        value="This user has no cases.", inline=True)
        embed.set_footer(text="React with ✅ to dismiss.")

    if invite:
        report_msg = await channel.send(f"{ping_string}\nMessage contained invite: {invite}", embed=embed)
    else:
        report_msg = await channel.send(ping_string, embed=embed)

    report_reactions = {'⚠️': handle_warn,
                        '🔇': handle_mute,
                        '❌': handle_ban,
                        '✅': handle_pass
                        }
    for reaction in report_reactions:
        await report_msg.add_reaction(reaction)

    def check(reaction, user):
        res = (user.id != bot.user.id
               and reaction.message == report_msg
               and str(reaction.emoji) in report_reactions
               and bot.settings.permissions.hasAtLeast(user.guild, user, 5))
        return res

    try:
        reaction, punisher = await bot.wait_for('reaction_add', timeout=120.0, check=check)
    except asyncio.TimeoutError:
        try:
            await report_msg.clear_reactions()
        except Exception:
            pass
    else:
        await report_msg.clear_reactions()
        callback = report_reactions[str(reaction.emoji)]
        await callback(bot, msg, punisher, user)
        await report_msg.delete()


async def handle_warn(bot, msg, punisher, user):
    channel = msg.guild.get_channel(bot.settings.guild().channel_reports)

    def response(message):
        # print(message.author.id == punisher.id)
        # print(user, punisher)
        return message.author.id == punisher.id
    
    ctx = msg.channel
    points = None
    reason = None
    while True:
        prompt = await ctx.send("Please enter points for the warn.")
        try:
            points = await bot.wait_for('message', check=response, timeout=30)
        except asyncio.TimeoutError:
            await prompt.delete()
            return
        else:
            try:
                await points.delete()
                points = int(points.content)
                await prompt.delete()
                if points > 0:
                    break
            except ValueError:
                pass
    
    while True:
        prompt = await ctx.send("Please enter a reason for the warn.")
        try:
            reason = await bot.wait_for('message', check=response, timeout=30)
        except asyncio.TimeoutError:
            await prompt.delete()
            return
        else:
            await reason.delete()
            reason = reason.content
            await prompt.delete()
            break
    
    await warn(bot, channel, punisher, user, points, reason)
    await msg.delete(delay=5)

async def handle_mute(bot, msg, punisher, user):
    pass


async def handle_ban(bot, msg, punisher, user):
    pass


async def handle_pass(bot, msg, punisher, user):
    try:
        await msg.delete()
    except Exception:
        pass


async def warn(bot, channel, punisher, user, points, reason):
    reason = discord.utils.escape_markdown(reason)
    reason = discord.utils.escape_mentions(reason)
    guild = bot.settings.guild()
    # prepare the case object for database
    case = Case(
        _id=guild.case_id,
        _type="WARN",
        mod_id=punisher.id,
        mod_tag=str(punisher),
        reason=reason,
        punishment=str(points)
    )

    # increment case ID in database for next available case ID
    await bot.settings.inc_caseid()
    # add new case to DB
    await bot.settings.add_case(user.id, case)
    # add warnpoints to the user in DB
    await bot.settings.inc_points(user.id, points)

    # fetch latest document about user from DB
    results = await bot.settings.user(user.id)
    cur_points = results.warn_points

    # prepare log embed, send to #public-mod-logs, user, channel where invoked
    log = await logging.prepare_warn_log(punisher, user, case)
    log.add_field(name="Current points", value=cur_points, inline=True)

    log_kickban = None

    # if cur_points >= 600:
    #     # automatically ban user if more than 600 points
    #     try:
    #         await user.send("You were banned from r/Jailbreak for reaching 600 or more points.", embed=log)
    #     except Exception:
    #         pass

    #     log_kickban = await self.add_ban_case(ctx, user, "600 or more warn points reached.")
    #     await user.ban(reason="600 or more warn points reached.")

    # elif cur_points >= 400 and not results.was_warn_kicked and isinstance(user, discord.Member):
    #     # kick user if >= 400 points and wasn't previously kicked
    #     await bot.settings.set_warn_kicked(user.id)

    #     try:
    #         await user.send("You were kicked from r/Jailbreak for reaching 400 or more points.", embed=log)
    #     except Exception:
    #         pass

    #     log_kickban = await self.add_kick_case(ctx, user, "400 or more warn points reached.")
    #     await user.kick(reason="400 or more warn points reached.")

    # else:
    if isinstance(user, discord.Member):
        try:
            await user.send("You were warned in r/Jailbreak.", embed=log)
        except Exception:
            pass

    # also send response in channel where command was called
    await channel.send(embed=log, delete_after=10)
    # await ctx.message.delete(delay=10)

    public_chan = channel.guild.get_channel(
        bot.settings.guild().channel_public)
    if public_chan:
        log.remove_author()
        log.set_thumbnail(url=user.avatar_url)
        await public_chan.send(embed=log)

        if log_kickban:
            log_kickban.remove_author()
            log_kickban.set_thumbnail(url=user.avatar_url)
            await public_chan.send(embed=log_kickban)
