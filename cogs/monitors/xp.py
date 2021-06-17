import math
import traceback
from random import randint

import discord
from discord.ext import commands
import cogs.utils.context as context


class Xp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        if member.bot:
            return
        if member.guild.id != self.bot.settings.guild_id:
            return

        user = await self.bot.settings.user(id=member.id)

        if user.is_xp_frozen or user.is_clem:
            return
        if member.guild.id != self.bot.settings.guild_id:
            return

        level = user.level

        db = self.bot.settings.guild()

        roles_to_add = await self.assess_new_roles(level, db)
        await self.add_new_roles(member, roles_to_add)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild:
            return
        if message.guild.id != self.bot.settings.guild_id:
            return
        if message.author.bot:
            return
        if message.channel.id == self.bot.settings.guild().channel_botspam:
            return

        user = await self.bot.settings.user(id=message.author.id)
        db = self.bot.settings.guild()
        if user.is_xp_frozen or user.is_clem:
            return

        xp_to_add = randint(0, 11)
        new_xp, level_before = await self.bot.settings.inc_xp(message.author.id, xp_to_add)
        new_level = await self.get_level(new_xp)

        if new_level > level_before:
            await self.bot.settings.inc_level(message.author.id)

        roles_to_add = await self.assess_new_roles(new_level, db)
        await self.add_new_roles(message, roles_to_add)

    async def assess_new_roles(self, new_level, db):
        roles_to_add = []
        if 15 <= new_level:
            roles_to_add.append(db.role_memberplus)
        if 30 <= new_level:
            roles_to_add.append(db.role_memberpro)
        if 50 <= new_level:
            roles_to_add.append(db.role_memberedition)
        if 75 <= new_level:
            roles_to_add.append(db.role_memberone)

        return roles_to_add

    async def add_new_roles(self, obj, roles_to_add):
        if roles_to_add is not None:
            if isinstance(obj, discord.Message):
                for role in roles_to_add:
                    role = obj.guild.get_role(role)
                    if role not in obj.author.roles:
                        await obj.author.add_roles(role)
            
            elif isinstance(obj, discord.Member):
                for role in roles_to_add:
                    role = obj.guild.get_role(role)
                    if role not in obj.roles:
                        await obj.add_roles(role)

    async def get_level(self, current_xp):
        level = 0
        xp = 0
        while xp <= current_xp:
            xp = xp + 45 * level * (math.floor(level / 10) + 1)
            level += 1
        return level

    async def info_error(self,  ctx: context.Context, error):
        if (isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.MissingPermissions)
                or isinstance(error, commands.NoPrivateMessage)):
            await ctx.send_error(error)
        else:
            traceback.print_exc()


def setup(bot):
    bot.add_cog(Xp(bot))
