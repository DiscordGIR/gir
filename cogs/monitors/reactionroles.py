import discord
from discord.ext import commands
import traceback
import asyncio


class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='addreaction', hidden=True)
    @commands.guild_only()
    async def addreaction(self, ctx: commands.Context, message_id: int):
        if not ctx.guild.id == self.bot.settings.guild_id:
            return
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 6):
            raise commands.BadArgument(
                "You do not have permission to use this command.")
        channel = ctx.guild.get_channel(self.bot.settings.guild().channel_reaction_roles)
        
        if channel is None:
            return
        
        message = None
        try:
            message = await channel.fetch_message(message_id)
        except Exception:
            raise commands.BadArgument("Message not found.")
        
        def check_msg(m):
            return m.author == ctx.author and m.channel == ctx.channel

        reaction_mapping = {message.id: {}}
        stack = [ctx.message]
        reactions = []
        
        async def delete_stack(the_stack):
            for m in the_stack:
                try:
                    await m.delete()
                except Exception:
                    pass
            return []
        
        while True:
            prompt_embed = await ctx.send("Add the reaction to this message that you want to watch for (or :white_check_mark: to stop).")
            stack.append(prompt_embed)
            def check_reaction(reaction, user):
                return user.id == ctx.author.id and reaction.message.id == prompt_embed.id
            
            try:
                reaction, _ = await self.bot.wait_for('reaction_add', timeout=120.0, check=check_reaction)
            except asyncio.TimeoutError:
                try:
                    stack = await delete_stack(stack)
                    return
                except Exception:
                    pass
            else:
                if str(reaction.emoji) == "✅":
                    stack = await delete_stack(stack)
                    break
                
                if isinstance (reaction.emoji, discord.PartialEmoji) or not (isinstance(reaction.emoji, discord.Emoji) and reaction.emoji.available):
                    stack = await delete_stack(stack)
                    await ctx.send("That emoji is not available to me :(", delete_after=5)
                    continue
                
                while True:
                    stack = await delete_stack(stack)
                    try:
                        prompt_role = await ctx.send("Please enter a role ID to use for this react (or 'cancel' to stop)")
                        stack.append(prompt_role)
                        role_id = await self.bot.wait_for('message', check=check_msg)
                        stack.append(role_id)
                    except asyncio.TimeoutError:
                        stack = await delete_stack(stack)
                        return
                    else:
                        if role_id.content == 'cancel':
                            stack = await delete_stack(stack)
                            return
                        the_role = ctx.guild.get_role(int(role_id.content))
                        if the_role is None:
                            stack = await delete_stack(stack)
                        else:
                            reaction_mapping[message.id][str(reaction.emoji)] = the_role.id
                            reactions.append(reaction)
                            stack = await delete_stack(stack)
                            break
                        
        print(reaction_mapping)
        await self.bot.settings.add_rero_mapping(reaction_mapping)
        the_string = "Done! We added the following emotes:\n"
        for r in reactions:
            the_string += f"Reaction {str(r)} will give role <@&{reaction_mapping[message.id][str(r.emoji)]}>\n"
            await message.add_reaction(r)
        await ctx.send(the_string, delete_after=5)
            

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
