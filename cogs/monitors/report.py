import discord
import asyncio

async def report(bot, msg, user):
    role = discord.utils.get(msg.guild.roles, id=bot.settings.guild().role_moderator)
    channel = discord.utils.get(msg.guild.channels, id=bot.settings.guild().channel_reports)
    
    ping_string = ""
    for member in role.members:
        offline_ping = (await bot.settings.user(member.id)).offline_report_ping
        if member.status == discord.Status.online or offline_ping:
            ping_string += f"{member.mention} "

    embed = discord.Embed(title="Word filter")
    embed.color = discord.Color.red()
    embed.description = ":warning:: Warn for 50 points\n:100:: Warn for 100 points"
    embed.add_field(name="Member", value=f"{user} ({user.mention})")
    embed.add_field(name="Channel", value=msg.channel.mention)
    embed.add_field(name="Message", value=discord.utils.escape_markdown(msg.content), inline=False)
    
    report_msg = await channel.send(ping_string, embed=embed)
    # report_reactions = ['⚠️', '💯']

    # for reaction in report_reactions:
    #     await report_msg.add_reaction(reaction)

    # def check(reaction, user):
    #     return (bot.settings.permissions.hasAtLeast(user.guild, user, 6) 
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