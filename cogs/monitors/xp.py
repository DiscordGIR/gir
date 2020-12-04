import traceback
from random import randint
import discord
import math
from discord.ext import commands


class Xp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        user = await self.bot.settings.user(id=member.id)

        if user.is_xp_frozen or user.is_clem:
            return
        if message.guild.id != self.bot.settings.guild_id:
            return
        
        level = user.level
        
        roles_to_add = []
        if 15 <= new_level:
            roles_to_add.append(self.bot.settings.guild().role_memberplus)
        if 30 <= new_level:
            roles_to_add.append(self.bot.settings.guild().role_memberpro)
        if 50 <= new_level:
            roles_to_add.append(self.bot.settings.guild().role_memberedition)

        print(roles_to_add)

        if roles_to_add is not None:
            for role in roles_to_add:
                role = member.guild.get_role(role)
                if role not in member.roles:
                    await member.add_roles(role)


    @commands.Cog.listener()
    async def on_message(self, message):
        user = await self.bot.settings.user(id=message.author.id)

        if user.is_xp_frozen or user.is_clem:
            return
        if message.guild.id != self.bot.settings.guild_id:
            return

        xp_to_add = randint(0, 11)
        print(f"giving {message.author} {xp_to_add}")
        new_xp, level_before = await self.bot.settings.inc_xp(message.author.id, xp_to_add)
        print(new_xp)
        print(level_before)
        new_level = await self.get_level(new_xp)
        print(new_level)
        if new_level > level_before:
            await self.bot.settings.inc_level(message.author.id)

        roles_to_add = []
        if 15 <= new_level:
            roles_to_add.append(self.bot.settings.guild().role_memberplus)
        if 30 <= new_level:
            roles_to_add.append(self.bot.settings.guild().role_memberpro)
        if 50 <= new_level:
            roles_to_add.append(self.bot.settings.guild().role_memberedition)

        print(roles_to_add)

        if roles_to_add is not None:
            for role in roles_to_add:
                role = message.guild.get_role(role)
                if role not in message.author.roles:
                    await message.author.add_roles(role)

    async def get_level(self, current_xp):
        level = 0
        xp = 0
        while xp <= current_xp:
            xp = xp + 45 * level * (math.floor(level / 10) + 1);
            level += 1
        return level

    async def info_error(self, ctx, error):
        if (isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.MissingPermissions)
                or isinstance(error, commands.NoPrivateMessage)):
            await self.bot.send_error(ctx, error)
        else:
            traceback.print_exc()


def setup(bot):
    bot.add_cog(Xp(bot))
