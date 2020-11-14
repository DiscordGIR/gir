import discord
from discord.ext import commands
from postgresql import Database
import asyncio

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot         = bot
        self.guild_id    = '777155838849843200'
        self.guilds      = Guilds(self)
        self.users       = Users(self)
        self.permissions = Permissions(self.bot, self.guild_id, self)
        self.roles       = Roles(self)
        self.channels    = Channels(self)
        self.db          = Database()
    
    async def setup(self):
        await self.db.init()
        await self.guilds.init()
        await self.users.init()
        await self.roles.init()
        await self.channels.init()

class Permissions:
    def __init__(self, bot, guild_id, settings):
        self.settings = settings
        self.permissions = {
            0: True,
            1: (lambda guild, m: guild.id == guild_id
                and settings.roles.memplus in m.roles),
            2: (lambda guild, m: guild.id == guild_id
                and settings.roles.mempro in m.roles),
            3: (lambda guild, m: guild.id == guild_id
                and settings.roles.memed in m.roles),
            4: (lambda guild, m: guild.id == guild_id
                and settings.roles.genius in m.roles),
            5: (lambda guild, m: guild.id == guild_id
                and m.guild_permissions.manage_guild),
            6: (lambda guild, m: guild.id == guild_id
                and settings.roles.moderator in m.roles),
            7: (lambda guild, m: guild.id == guild_id
                and m == guild.owner),
            8: (lambda guild, m: guild.id == guild_id
                and m == bot.owner)
        }
    
    def hasAtLeast(self, guild, member, level):
        return self.permissions[level](guild, member)

class Guilds:
    class Guild:
        def __init__(self, guild):
            self.guild = guild
        
        def get(self, key):
            return self.guild[key]

    def __init__(self, settings):
        self.guilds = { }
        self.settings = settings
    
    def get(self, id):
        return self.guilds[id]
    
    async def init(self):
        for record in await self.settings.db.get("guilds"):
            self.guilds[record.get('id')] = { }
            for key in record.keys():
                if key != "id":
                    self.guilds[record.get('id')][key] = record[key]
class Users:
    class User:
        def __init__(self, user):
            self.user = user

        def get(self, key):
            return self.user[key]

        def _set(self, key, value):
            self.user[key] = value  

        def increment(self, key, incr):
            self.user[key] += incr

        def increment_and_get(self, key, incr):
            self.user[key] += incr
            return self.user[key]  
    
    def __init__(self, settings):
        self.settings = settings
        self.users = { }

    async def init(self):
        for record in await self.settings.db.get("users"):
            self.users[record.get('id')] = { }
            for key in record.keys():
                if key != "id":
                    self.users[record.get('id')][key] = record[key]
            
    def get(self, id):
        return self.users[id]

class Channels:
    def __init__(self, settings):
        self.settings = settings
        self.public     = None 
        self.private    = None 
        self.reports    = None 

    async def init(self):
        self.public      = self.settings.guilds.get(self.settings.guild_id).get('channels.public')
        self.private     = self.settings.guilds.get(self.settings.guild_id).get('channels.private')
        self.reports     = self.settings.guilds.get(self.settings.guild_id).get('channels.reports')

class Roles:
    def __init__(self, settings):
        self.memplus   = None
        self.mempro    = None
        self.memed     = None
        self.genius    = None
        self.moderator = None
        self.settings  = settings

    async def init(self):
        self.memplus   = self.settings.guilds.get(self.settings.guild_id).get("roles.memberplus")
        self.mempro    = self.settings.guilds.get(self.settings.guild_id).get("roles.memberplus")
        self.memed     = self.settings.guilds.get(self.settings.guild_id).get("roles.memberedition")
        self.genius    = self.settings.guilds.get(self.settings.guild_id).get("roles.genius")
        self.moderator = self.settings.guilds.get(self.settings.guild_id).get("roles.moderator")


# insert into guilds VALUES ('777155838849843200', '!', 'enUS', 'FALSE', '{}', '777270186604101652', '777270163589693482', '777270163589693482', '777270542033092638', '777270554800422943', '777270579719569410', '777155838849843204', FALSE, FALSE, '{}', '{}', '777270242874359828', '777270206841880586', '777270222868185158', '{}', '777270914365784075');