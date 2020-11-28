import discord

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
    embed.add_field(name="Member", value=f"{user} ({user.mention})")
    embed.add_field(name="Channel", value=msg.channel.mention)
    embed.add_field(name="Message", value=discord.utils.escape_markdown(msg.content), inline=False)
    await channel.send(ping_string, embed=embed)
