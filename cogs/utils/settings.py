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
        return User.objects(_id=id).modify(upsert=True, new=True, 
            set_on_insert___id=id,  set_on_insert__is_clem=False,
             set_on_insert__was_warn_kicked=False,  set_on_insert__xp=0,
              set_on_insert__level=0,  set_on_insert__offline_report_ping=False, 
              set_on_insert__warn_points=0)
    
    async def cases(self, id):
        return Cases.objects(_id=id).modify(upsert=True, new=True,
             set_on_insert___id=id, set_on_insert__cases=[])
    
#     def __init__(self, bot):
#         self.bot         = bot
#         self.guild_id    = int(os.environ.get("BOTTY_MAINGUILD"))
#         self.guilds      = Guilds(self)
#         # self.users       = Users(self)
#         self.permissions = Permissions(self.bot, self)
#         self.roles       = Roles(self)
#         self.channels    = Channels(self)
#         self.db          = Database()
        
#         bot.loop.run_until_complete(self.cog_load())

#     async def cog_load(self):
#         await self.db.init()
#         await self.guilds.init()
#         # await self.users.init()
#         await self.roles.init()
#         await self.channels.init()
#         print("Loaded settings from database!")

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

# class Guilds:
#     class Guild:
#         def __init__(self, guild):
#             self.guild = guild
        
#         def get(self, key):
#             return self.guild[key]

#     def __init__(self, settings):
#         self.guilds = { }
#         self.settings = settings
    
#     def get(self, id):
#         return self.guilds[id]
    
#     async def init(self):
#         for record in await self.settings.db.get("guilds"):
#             self.guilds[int(record.get('id'))] = { }
#             for key in record.keys():
#                 if key != "id":
#                     self.guilds[int(record.get('id'))][key] = record[key]
# # class Users:
# #     class User:
# #         def __init__(self, user):
# #             self.user = user

# #         def get(self, key):
# #             return self.user[key]

# #         def _set(self, key, value):
# #             self.user[key] = value  

# #         def increment(self, key, incr):
# #             self.user[key] += incr

# #         def increment_and_get(self, key, incr):
# #             self.user[key] += incr
# #             return self.user[key]  
    
# #     def __init__(self, settings):
# #         self.settings = settings
# #         self.users = { }

# #     async def init(self):
# #         for record in await self.settings.db.get("users"):
# #             self.users[record.get('id')] = { }
# #             for key in record.keys():
# #                 if key != "id":
# #                     self.users[record.get('id')][key] = record[key]
            
# #     def get(self, id):
# #         return self.users[id]

# class Channels:
#     def __init__(self, settings):
#         self.settings = settings
#         self.public     = None 
#         self.private    = None 
#         self.reports    = None 

#     async def init(self):
#         self.public      = int(self.settings.guilds.get(self.settings.guild_id).get('channels.public'))
#         self.private     = int(self.settings.guilds.get(self.settings.guild_id).get('channels.private'))
#         self.reports     = int(self.settings.guilds.get(self.settings.guild_id).get('channels.reports'))

# class Roles:
#     def __init__(self, settings):
#         self.memplus   = None
#         self.mempro    = None
#         self.memed     = None
#         self.genius    = None
#         self.moderator = None
#         self.settings  = settings

#     async def init(self):
#         self.memplus   = int(self.settings.guilds.get(self.settings.guild_id).get("roles.memberplus"))
#         self.mempro    = int(self.settings.guilds.get(self.settings.guild_id).get("roles.memberplus"))
#         self.memed     = int(self.settings.guilds.get(self.settings.guild_id).get("roles.memberedition"))
#         self.genius    = int(self.settings.guilds.get(self.settings.guild_id).get("roles.genius"))
#         self.moderator = int(self.settings.guilds.get(self.settings.guild_id).get("roles.moderator"))


# insert into guilds VALUES ('777155838849843200', '!', 'enUS', 'FALSE', '{}', '777270186604101652', '777270163589693482', '777270163589693482', '777270542033092638', '777270554800422943', '777270579719569410', '777155838849843204', FALSE, FALSE, '{}', '{}', '777270242874359828', '777270206841880586', '777270222868185158', '{}', '777270914365784075');

def setup(bot):
    bot.add_cog(Settings(bot))