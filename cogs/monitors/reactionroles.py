import discord
from discord.ext import commands
import traceback
import asyncio


class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='addreaction', hidden=True)
    @commands.guild_only()
    async def addreaction(self, ctx: commands.Context, message: int):
        if not ctx.guild.id == self.bot.settings.guild_id:
            return
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 6):
            raise commands.BadArgument(
                "You do not have permission to use this command.")
        channel = ctx.guild.get_channel(self.bot.settings.guild().channel_reaction_roles)
        message = None
        try:
            message = await channel.fetch_message(message)
        except Exception:
            raise commands.BadArgument("Message not found.")
        
        def check_msg(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        def check_reaction(reaction, user):
            return user == ctx.author and reaction.message == ctx.message

        reaction_mapping = {message.id: {}}
        reactions = []
        prompt_embed = await ctx.send("Add the reaction to this message that you want to watch for (or :white_check_mark: to stop).")
        while True:
            try:
                reaction, _ = await bot.wait_for('reaction_add', timeout=120.0, check=check_msg)
            except asyncio.TimeoutError:
                try:
                    await prompt_embed.delete()
                    await ctx.message.delete()
                    return
                except Exception:
                    pass
            else:
                while True:
                    try:
                        prompt_role = await ctx.send("Please enter a role ID to use for this react (or 'cancel' to stop)")
                        role_id = await self.bot.wait_for('message', check=check_role)
                    except asyncio.TimeoutError:
                        await prompt_embed.delete()
                        await ctx.message.delete()
                        return
                    else:
                        if role_id == 'cancel':
                            await prompt_embed.delete()
                            await ctx.message.delete()
                            await prompt_role.delete()
                            return
                        the_role = ctx.guild.get_role(role_id)
                        if the_role is None:
                            await prompt_role.delete()
                        else:
                            reaction_mapping[message.id][reaction.id] = role_id
                            reactions += reaction
                            await prompt_role.delete()
                            break

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        pass
    
    @addreaction.error
    async def info_error(self, ctx, error):
        await ctx.message.delete(delay=5)
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
    bot.add_cog(ReactionRoles(bot))
