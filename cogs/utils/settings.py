import discord
from discord.ext import commands


class Settings(commands.Cog):
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

    def __init__(self, bot):
        self.guild_id = 777155838849843200
        guild         = bot.get_guild(self.guild_id)
        self.roles    = {
            "Muted"  : guild.get_role(123345),
            "MemPlus": guild.get_role(123345),
            "MemPro" : guild.get_role(123345),
            "MemEd"  : guild.get_role(123345),
            "Genius" : guild.get_role(123345),
            "Mod"    : guild.get_role(123345)
        }
        self.guilds = None
        self.public_logging_channel = guild.get_channel(688125770186489888)
        self.logging_channel        = guild.get_channel(688125770186489888)
        self.reports_channel        = guild.get_channel(688125770186489888)
        self.permissions            = Permissions(bot, self.guild_id, self.roles)
        self.clemmed_users          = []

class Permissions:
    def __init__(self, bot, guild_id, roles):
        self.permissions = {
            0: True,
            1: (lambda guild, m: guild.id == guild_id
                and roles["MemPlus"] in m.roles),
            2: (lambda guild, m: guild.id == guild_id
                and roles["MemPro"] in m.roles),
            3: (lambda guild, m: guild.id == guild_id
                and roles["MemEd"] in m.roles),
            4: (lambda guild, m: guild.id == guild_id
                and roles["Genius"] in m.roles),
            5: (lambda guild, m: guild.id == guild_id
                and m.guild_permissions.manage_guild),
            6: (lambda guild, m: guild.id == guild_id
                and roles["Mod"] in m.roles),
            7: (lambda guild, m: guild.id == guild_id
                and m == guild.owner),
            8: (lambda guild, m: guild.id == guild_id
                and m == bot.owner)
        }
    
    def hasAtLeast(self, guild, member, level):
        return self.permissions[level](guild, member)
