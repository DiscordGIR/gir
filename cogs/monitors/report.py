import asyncio
import datetime
from discord.ext import commands
import pytimeparse
import cogs.utils.context as context

import discord
import humanize


async def report(bot, msg, user, word, invite=None):
    channel = msg.guild.get_channel(bot.settings.guild().channel_reports)
    ping_string = await prepare_ping_string(bot, msg)
    embed = await prepare_embed(bot, user, msg, word)

    if invite:
        report_msg = await channel.send(f"{ping_string}\nMessage contained invite: {invite}", embed=embed)
    else:
        report_msg = await channel.send(ping_string, embed=embed)
    report_reactions = ['✅', '🆔', '🧹']

    ctx = await bot.get_context(report_msg, cls=context.Context)
    prompt_data = context.PromptDataReaction(report_msg, report_reactions)
    
    while True:
        reaction, reactor = await ctx.prompt_reaction(prompt_data)
        if not bot.settings.permissions.hasAtLeast(user.guild, user, 5) or reaction not in report_reactions:
            await report_msg.remove_reaction(reaction, reactor)
    
        if reaction == '✅':
            try:
                await report_msg.delete()
            except Exception:
                pass
            return
        elif reaction == '🆔':
            await channel.send(user.id)
        elif reaction == '🧹':
            await channel.purge(limit=100)
            return


async def report_spam(bot, msg, user, title):
    channel = msg.guild.get_channel(bot.settings.guild().channel_reports)
    ping_string = await prepare_ping_string(bot, msg)    
    
    embed = await prepare_embed(bot, user, msg, title=title)
    embed.set_footer(text="✅ to pardon, 💀 to ban, ⚠️ to temp mute.")
    
    report_msg = await channel.send(ping_string, embed=embed)
    report_reactions = ['✅', '💀', '⚠️']

    ctx = await bot.get_context(report_msg, cls=context.Context)
    prompt_data = context.PromptDataReaction(report_msg, report_reactions)
    
    while True:
        reaction, reactor = await ctx.prompt_reaction(prompt_data)
        if not bot.settings.permissions.hasAtLeast(user.guild, user, 5) or reaction not in report_reactions:
            await report_msg.remove_reaction(reaction, reactor)
            
        if reaction == '✅':
            ctx.author = ctx.message.author = reactor
            unmute = bot.get_command("unmute")
            if unmute is not None:
                try:
                    await unmute(ctx=ctx, user=user, reason="Reviewed by a moderator.")
                except Exception:
                    pass
                await report_msg.delete()
            else:
                await ctx.send_warning("I wasn't able to unmute them.")
            return
        
        elif reaction == '💀':
            ctx.author = ctx.message.author = reactor
            ban = bot.get_command("ban")
            if ban is not None:
                try:
                    await ban(ctx=ctx, user=user, reason="Ping spam")
                except Exception:
                    pass
                await report_msg.delete()
            else:
                await ctx.send_warning("I wasn't able to ban them.")
            return
        elif reaction == '⚠️':            
            ctx.author = ctx.message.author = reactor
            now = datetime.datetime.now()
            delta = await prompt_time(ctx)
            if delta is None:
                continue
            
            try:
                time = now + datetime.timedelta(seconds=delta)
                ctx.tasks.schedule_unmute(user.id, time)
                
                await ctx.send_success(title="Done!", description=f"{user.mention} was muted for {humanize.naturaldelta(time - now)}.", delete_after=5)
                await report_msg.delete()
                
                try:
                    await user.send(embed=discord.Embed(title="Ping spam unmute", description=f"A moderator has reviewed your ping spam report. You will be unmuted in {humanize.naturaldelta(time - now)}.", color=discord.Color.orange()))
                except Exception:
                    pass
                
                return
            except Exception:
                return

async def prompt_time(ctx):
    prompt_data = context.PromptData(value_name="duration", 
                                     description="Please enter a duration for the mute (i.e 15m).",
                                     convertor=pytimeparse.parse,
                                     )
    return await ctx.prompt(prompt_data)

async def report_raid(bot, user, msg=None):
    embed = discord.Embed()
    embed.title = "Possible raid occurring"
    embed.description = "The raid filter has been triggered 5 or more times in the past 10 seconds. I am automatically locking all the channels. Use `!unfreeze` when you're done."
    embed.color = discord.Color.red()
    embed.set_thumbnail(url=user.avatar_url)
    embed.add_field(name="Member", value=f"{user} ({user.mention})")
    if msg is not None:
        embed.add_field(name="Message", value=msg.content, inline=False)

    reports_channel = user.guild.get_channel(bot.settings.guild().channel_reports)
    await reports_channel.send(f"<@&{bot.settings.guild().role_moderator}>", embed=embed, allowed_mentions=discord.AllowedMentions(roles=True))


async def prepare_embed(bot, user, msg, word=None, title="Word filter"):
    user_info = await bot.settings.user(user.id)
    joined = user.joined_at.strftime("%B %d, %Y, %I:%M %p")
    created = user.created_at.strftime("%B %d, %Y, %I:%M %p")
    rd = await bot.settings.rundown(user.id)
    rd_text = ""
    for r in rd:
        if r._type == "WARN":
            r.punishment += " points"
        rd_text += f"**{r._type}** - {r.punishment} - {r.reason} - {humanize.naturaltime(datetime.datetime.now() - r.date)}\n"

    embed = discord.Embed(title=title)
    embed.color = discord.Color.red()

    embed.set_thumbnail(url=user.avatar_url)
    embed.add_field(name="Member", value=f"{user} ({user.mention})")
    embed.add_field(name="Channel", value=msg.channel.mention)

    if len(msg.content) > 400:
        msg.content = msg.content[0:400] + "..."

    if word is not None:
        embed.add_field(name="Message", value=discord.utils.escape_markdown(
            msg.content) + f"\n\n[Link to message]({msg.jump_url}) | Filtered word: **{word}**", inline=False)
    else:
        embed.add_field(name="Message", value=discord.utils.escape_markdown(
            msg.content) + f"\n\n[Link to message]({msg.jump_url})", inline=False)
    embed.add_field(name="Join date", value=f"{joined} UTC", inline=True)
    embed.add_field(name="Account creation date",
                    value=f"{created} UTC", inline=True)
    embed.add_field(name="Warn points",
                    value=user_info.warn_points, inline=True)

    reversed_roles = user.roles
    reversed_roles.reverse()

    roles = ""
    for role in reversed_roles[0:4]:
        if role != user.guild.default_role:
            roles += role.mention + " "
    roles = roles.strip() + "..."

    embed.add_field(
        name="Roles", value=roles if roles else "None", inline=False)

    if len(rd) > 0:
        embed.add_field(name=f"{len(rd)} most recent cases",
                        value=rd_text, inline=True)
    else:
        embed.add_field(name=f"Recent cases",
                        value="This user has no cases.", inline=True)
    embed.set_footer(text="React with ✅ to dismiss.")
    return embed


async def prepare_ping_string(bot, msg):
    ping_string = ""    
    role = msg.guild.get_role(bot.settings.guild().role_moderator)
    for member in role.members:
        offline_ping = (await bot.settings.user(member.id)).offline_report_ping
        if member.status == discord.Status.online or offline_ping:
            ping_string += f"{member.mention} "

    return ping_string