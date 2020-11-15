import discord
from discord.ext import commands
import asyncio
import json

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot         = bot
        self.guild_id    = 777155838849843200
        self.guilds      = Guilds(self)
        self.users       = Users(self)
        self.permissions = Permissions(self.bot, self)
        self.roles       = Roles(self)
        self.channels    = Channels(self)
        self.db          = Database()
        
        bot.loop.run_until_complete(self.cog_load())

    async def cog_load(self):
        await self.db.init()
        await self.guilds.init()
        await self.users.init()
        await self.roles.init()
        await self.channels.init()
        print("done")

class Permissions:
    def __init__(self, bot, settings):
        self.bot = bot
        self.settings = settings
        guild_id = self.settings.guild_id
        self.permissions = {
            0: lambda x, y: True,
            1: (lambda guild, m: guild.id == guild_id
                and discord.utils.get(guild.roles, id=settings.roles.memplus) in m.roles),
            2: (lambda guild, m: guild.id == guild_id
                and discord.utils.get(guild.roles, id=settings.roles.mempro) in m.roles),
            3: (lambda guild, m: guild.id == guild_id
                and discord.utils.get(guild.roles, id=settings.roles.memed) in m.roles),
            4: (lambda guild, m: guild.id == guild_id
                and discord.utils.get(guild.roles, id=settings.roles.genius) in m.roles),
            5: (lambda guild, m: guild.id == guild_id
                and m.guild_permissions.manage_guild),
            6: (lambda guild, m: guild.id == guild_id
                and discord.utils.get(guild.roles, id=settings.roles.moderator) in m.roles),
            7: (lambda guild, m: guild.id == guild_id
                and m == guild.owner),
            8: (lambda guild, m: guild.id == guild_id
                and m.id == bot.owner_id)
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
            self.guilds[int(record.get('id'))] = { }
            for key in record.keys():
                if key != "id":
                    self.guilds[int(record.get('id'))][key] = record[key]
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
        self.public      = int(self.settings.guilds.get(self.settings.guild_id).get('channels.public'))
        self.private     = int(self.settings.guilds.get(self.settings.guild_id).get('channels.private'))
        self.reports     = int(self.settings.guilds.get(self.settings.guild_id).get('channels.reports'))

class Roles:
    def __init__(self, settings):
        self.memplus   = None
        self.mempro    = None
        self.memed     = None
        self.genius    = None
        self.moderator = None
        self.settings  = settings

    async def init(self):
        self.memplus   = int(self.settings.guilds.get(self.settings.guild_id).get("roles.memberplus"))
        self.mempro    = int(self.settings.guilds.get(self.settings.guild_id).get("roles.memberplus"))
        self.memed     = int(self.settings.guilds.get(self.settings.guild_id).get("roles.memberedition"))
        self.genius    = int(self.settings.guilds.get(self.settings.guild_id).get("roles.genius"))
        self.moderator = int(self.settings.guilds.get(self.settings.guild_id).get("roles.moderator"))


# insert into guilds VALUES ('777155838849843200', '!', 'enUS', 'FALSE', '{}', '777270186604101652', '777270163589693482', '777270163589693482', '777270542033092638', '777270554800422943', '777270579719569410', '777155838849843204', FALSE, FALSE, '{}', '{}', '777270242874359828', '777270206841880586', '777270222868185158', '{}', '777270914365784075');
import asyncpg

class Database:
    async def init(self):
        self.conn = await asyncpg.connect(
            host     = "127.0.0.1",
            database = "janet",
            user     = "emy"
        )

    async def get(self, table):
        stmt = await self.conn.prepare(f'SELECT * FROM "{table}"')
        return await stmt.fetch()

    async def get_with_id(self, table, _id):
        stmt = await self.conn.prepare(f'SELECT * FROM "{table}" WHERE id = $1')
        return await stmt.fetch(str(_id))

    async def get_with_key(self, table, key):
        stmt = await self.conn.prepare(f'SELECT "{key}" FROM {table}')
        return await stmt.fetch()
        
    async def get_with_key_and_id(self, table, key, _id):
        stmt = await self.conn.prepare(f'SELECT "{key}" FROM {table} WHERE id = $1')
        return await stmt.fetch(str(_id))

    async def append_json(self, table, key, _id, _json):
        _json = str(json.dumps(_json))
        await self.conn.execute(f'INSERT INTO "{table}" (id, {key}) VALUES($2, array[$1::json]) ON CONFLICT (id) DO UPDATE SET {key} = EXCLUDED.{key} || $1::json WHERE EXCLUDED.id = $2', _json, str(_id))

    async def set_with_key_and_id(self, table, key, _id, val):
        await self.conn.execute(f'UPDATE "{table}" SET "{key}" = $1 WHERE id = $2', val, str(_id))

    async def increment_and_get(self, table, key, _id, val):
        return await self.conn.fetch(f'UPDATE "{table}" SET "{key}" = "{key}" + $1 WHERE id = $2 RETURNING *', int(val), str(_id))

def setup(bot):
    bot.add_cog(Settings(bot))