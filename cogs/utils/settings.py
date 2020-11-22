import discord
from discord.ext import commands
import asyncio
import json
import data.mongo_setup as mongo_setup
import os
from data.guild import Guild
from data.cases import Cases
from data.user import User

class Settings(commands.Cog):
    def __init__(self, bot):
        mongo_setup.global_init()
        print("Loaded database")
        self.bot = bot
        self.guild_id    = int(os.environ.get("BOTTY_MAINGUILD"))
        self.permissions = Permissions(self.bot, self)

    def guild(self):
        return Guild.objects(_id=self.guild_id).first()

    async def inc_caseid(self):
        Guild.objects(_id=self.guild_id).update_one(inc__case_id=1)

    async def add_case(self, _id, case):
        await self.cases(_id)
        Cases.objects(_id=_id).update_one(push__cases=case)

    async def inc_points(self, _id, points):
        await self.user(_id)
        User.objects(_id=_id).update_one(inc__warn_points=points)

    async def set_warn_kicked(self, _id):
        await self.user(_id)
        User.objects(_id=_id).update_one(set__was_warn_kicked=True)
        
    async def user(self, id):
        # return User.objects(_id=id).modify(upsert=True, new=True, 
        #     set_on_insert___id=id,  set_on_insert__is_clem=False,
        #      set_on_insert__was_warn_kicked=False,  set_on_insert__xp=0,
        #       set_on_insert__level=0,  set_on_insert__offline_report_ping=False, 
        #       set_on_insert__warn_points=0)
        user = User.objects(_id=id).first()
        if not user:
            user = User()
            user._id = id
            user.save()
        return user
    
    async def cases(self, id):
        # return Cases.objects(_id=id).modify(upsert=True, new=True,
        #      set_on_insert___id=id, set_on_insert__cases=[])

        cases = Cases.objects(_id=id).first()
        if cases is None:
            cases = Cases()
            cases._id = id
            cases.save()
        return cases

class Permissions:
    def __init__(self, bot, settings):
        self.bot = bot
        self.settings = settings
        guild_id = self.settings.guild_id
        the_guild = settings.guild()
        self.permissions = {
            0: lambda x, y: True,
            1: (lambda guild, m: guild.id == guild_id
                and discord.utils.get(guild.roles, id=the_guild.role_memberplus) in m.roles),
            2: (lambda guild, m: guild.id == guild_id
                and discord.utils.get(guild.roles, id=the_guild.role_memberpro) in m.roles),
            3: (lambda guild, m: guild.id == guild_id
                and discord.utils.get(guild.roles, id=the_guild.role_memberedition) in m.roles),
            4: (lambda guild, m: guild.id == guild_id
                and discord.utils.get(guild.roles, id=the_guild.role_memberpro) in m.roles),
            5: (lambda guild, m: guild.id == guild_id
                and m.guild_permissions.manage_guild),
            6: (lambda guild, m: guild.id == guild_id
                and discord.utils.get(guild.roles, id=the_guild.role_moderator) in m.roles),
            7: (lambda guild, m: guild.id == guild_id
                and m == guild.owner),
        
            8: (lambda guild, m: guild.id == guild_id
                and m.id == bot.owner_id)
        }
    
    def hasAtLeast(self, guild, member, level):
        return self.permissions[level](guild, member)

def setup(bot):
    bot.add_cog(Settings(bot))