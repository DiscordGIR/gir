import discord
from discord.ext import commands


class Settings(commands.Cog):
    def __init__(self, bot):
        self.guild_id    = 777155838849843200
        self.guilds      = Guilds()
        self.users       = Users()
        self.permissions = Permissions(bot, self.guild_id, self)
        self.roles       = Roles(self)
        self.channels    = Channels(self)

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

    def __init__(self):
        self.guilds = { }
    
    def get(self, id):
        return self.guilds[id]
    
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
    
    def __init__(self):
        self.guilds = { }
    
    def get(self, id):
        return self.guilds[id]

class Channels:
    def __init__(self, settings):
        self.public      = settings.guilds.get(settings.guild_id).get('channels.public')
        self.private     = settings.guilds.get(settings.guild_id).get('channels.private')
        self.reports     = settings.guilds.get(settings.guild_id).get('channels.reports')

class Roles:
    def __init__(self, settings):
        self.memplus   = settings.guilds.get(settings.guild_id).get("roles.memberplus")
        self.mempro    = settings.guilds.get(settings.guild_id).get("roles.memberplus")
        self.memed     = settings.guilds.get(settings.guild_id).get("roles.memberedition")
        self.genius    = settings.guilds.get(settings.guild_id).get("roles.genius")
        self.moderator = settings.guilds.get(settings.guild_id).get("roles.moderator")