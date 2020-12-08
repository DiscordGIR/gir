import discord


async def prepare_warn_log(author, user, case):
    embed = discord.Embed(title="Member warned")
    embed.set_author(name=user, icon_url=user.avatar_url)
    embed.color = discord.Color.orange()
    embed.add_field(name="Member", value=f'{user} ({user.mention})', inline=True)
    embed.add_field(name="Mod", value=f'{author} ({author.mention})', inline=True)
    embed.add_field(name="Increase", value=case.punishment, inline=True)
    embed.add_field(name="Reason", value=case.reason, inline=True)
    embed.set_footer(text=f"Case #{case._id} | {user.id}")
    return embed


async def prepare_liftwarn_log(author, user, case):
    embed = discord.Embed(title="Member warn lifted")
    embed.set_author(name=user, icon_url=user.avatar_url)
    embed.color = discord.Color.blurple()
    embed.add_field(name="Member", value=f'{user} ({user.mention})', inline=True)
    embed.add_field(name="Mod", value=f'{author} ({author.mention})', inline=True)
    embed.add_field(name="Decrease", value=case.punishment, inline=True)
    embed.add_field(name="Reason", value=case.lifted_reason, inline=True)
    embed.set_footer(text=f"Case #{case._id} | {user.id}")
    return embed


async def prepare_removepoints_log(author, user, case):
    embed = discord.Embed(title="Member points removed")
    embed.set_author(name=user, icon_url=user.avatar_url)
    embed.color = discord.Color.blurple()
    embed.add_field(name="Member", value=f'{user} ({user.mention})', inline=True)
    embed.add_field(name="Mod", value=f'{author} ({author.mention})', inline=True)
    embed.add_field(name="Decrease", value=case.punishment, inline=True)
    embed.add_field(name="Reason", value=case.reason, inline=True)
    # embed.set_footer(text=f"Case #{case._id} | {user.id}")
    return embed


async def prepare_ban_log(author, user, case):
    embed = discord.Embed(title="Member banned")
    embed.color = discord.Color.blue()
    embed.set_author(name=user, icon_url=user.avatar_url)
    embed.add_field(name="Member", value=f'{user} ({user.mention})', inline=True)
    embed.add_field(name="Mod", value=f'{author} ({author.mention})', inline=True)
    embed.add_field(name="Reason", value=case.reason, inline=True)
    embed.set_footer(text=f"Case #{case._id} | {user.id}")
    return embed


async def prepare_unban_log(author, user, case):
    embed = discord.Embed(title="Member unbanned")
    embed.color = discord.Color.blurple()
    embed.set_author(name=user, icon_url=user.avatar_url)
    embed.add_field(name="Member", value=f'{user} ({user.id})', inline=True)
    embed.add_field(name="Mod", value=f'{author} ({author.mention})', inline=True)
    embed.add_field(name="Reason", value=case.reason, inline=True)
    embed.set_footer(text=f"Case #{case._id} | {user.id}")
    return embed


async def prepare_kick_log(author, user, case):
    embed = discord.Embed(title="Member kicked")
    embed.color = discord.Color.green()
    embed.set_author(name=user, icon_url=user.avatar_url)
    embed.add_field(name="Member", value=f'{user} ({user.mention})', inline=True)
    embed.add_field(name="Mod", value=f'{author} ({author.mention})', inline=True)
    embed.add_field(name="Reason", value=case.reason, inline=False)
    embed.set_footer(text=f"Case #{case._id} | {user.id}")
    return embed


async def prepare_mute_log(author, user, case):
    embed = discord.Embed(title="Member muted")
    embed.color = discord.Color.red()
    embed.set_author(name=user, icon_url=user.avatar_url)
    embed.add_field(name="Member", value=f'{user} ({user.mention})', inline=True)
    embed.add_field(name="Mod", value=f'{author} ({author.mention})', inline=True)
    embed.add_field(name="Duration", value=case.punishment, inline=True)
    embed.add_field(name="Reason", value=case.reason, inline=True)
    embed.set_footer(text=f"Case #{case._id} | {user.id}")
    return embed


async def prepare_unmute_log(author, user, case):
    embed = discord.Embed(title="Member unmuted")
    embed.color = discord.Color.green()
    embed.set_author(name=user, icon_url=user.avatar_url)
    embed.add_field(name="Member", value=f'{user} ({user.mention})', inline=True)
    embed.add_field(name="Mod", value=f'{author} ({author.mention})', inline=True)
    embed.add_field(name="Reason", value=case.reason, inline=True)
    embed.set_footer(text=f"Case #{case._id} | {user.id}")
    return embed
