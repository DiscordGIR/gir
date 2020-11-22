import discord

async def prepare_warn_log(ctx, user, case):
    embed=discord.Embed(title="Member warned")
    embed.set_author(name=user, icon_url=user.avatar_url)
    embed.add_field(name="Member", value=f'{user} ({user.mention})', inline=True)
    embed.add_field(name="Mod", value=f'{ctx.author} ({ctx.author.mention})', inline=True)
    embed.add_field(name="Increase", value=case.punishment, inline=True)
    embed.add_field(name="Reason", value=case.reason, inline=True)
    embed.set_footer(text=f"Case #{case._id} | Warned by {ctx.author}")
    return embed

async def prepare_ban_log(ctx, user, case):
    embed=discord.Embed(title="Member banned")
    embed.set_author(name=user, icon_url=user.avatar_url)
    embed.add_field(name="Member", value=f'{user} ({user.mention})', inline=True)
    embed.add_field(name="Mod", value=f'{ctx.author} ({ctx.author.mention})', inline=True)
    embed.add_field(name="Reason", value=case.reason, inline=True)
    embed.set_footer(text=f"Case #{case._id} | Banned by {ctx.author}")
    return embed

async def prepare_kick_log(ctx, user, case):
    embed=discord.Embed(title="Member kicked")
    embed.set_author(name=user, icon_url=user.avatar_url)
    embed.add_field(name="Member", value=f'{user} ({user.mention})', inline=True)
    embed.add_field(name="Mod", value=f'{ctx.author} ({ctx.author.mention})', inline=True)
    embed.add_field(name="Reason", value=case.reason, inline=False)
    embed.set_footer(text=f"Case #{case._id} | Kicked by {ctx.author}")
    return embed

# async def prepare_ban_log(ctx, user, case):
#     embed=discord.Embed(title="Member warned")
#     embed.set_author(name=user, icon_url=user.avatar_url)
#     embed.add_field(name="Member", value=f'{user} ({user.mention})', inline=True)
#     embed.add_field(name="Mod", value=f'{ctx.author} ({ctx.author.mention})', inline=True)
#     embed.add_field(name="Reason", value=case.reason, inline=True)
#     embed.set_footer(text=f"Case #{case.id} | Banned by {ctx.author}")
#     return embed