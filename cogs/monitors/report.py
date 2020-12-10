import asyncio
import datetime

import discord
import humanize


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
    # report_reactions = ['⚠️', '💯']

    # for reaction in report_reactions:
    #     await report_msg.add_reaction(reaction)
    await report_msg.add_reaction("✅")

    def check(reaction, user):
        res = (user.id != bot.user.id
               and reaction.message == report_msg
               and str(reaction.emoji) == "✅"
               and bot.settings.permissions.hasAtLeast(user.guild, user, 5))
        # if not res:
        #     await reaction.remove(user)
        return res

    try:
        reaction, _ = await bot.wait_for('reaction_add', timeout=120.0, check=check)
    except asyncio.TimeoutError:
        try:
            await report_msg.clear_reactions()
        except Exception:
            pass
    else:
        try:
            await report_msg.delete()
        except Exception:
            pass

    # def check(reaction, user):
    #     return (bot.settings.permissions.hasAtLeast(user.guild, user, 5)
    #         and reaction.message == report_msg
    #         and str(reaction.emoji) in report_reactions)

    # def check_2(reason_text, user):
    #     return
    # try:
    #     reaction, warner = await bot.wait_for('reaction_add', timeout=120.0, check=check)
    # except asyncio.TimeoutError:
    #     await report_msg.clear_reactions()
    # else:
    #     await report_msg.clear_reactions()

    #      try:
    #         reaction, user = await bot.wait_for('message', timeout=30.0, check=check2)
    #     except asyncio.TimeoutError:
    #         await report_msg.clear_reactions()
    #     else:

    #     cmd = bot.get_command("warn")
    #     await ctx.invoke(cmd, user, 50)
