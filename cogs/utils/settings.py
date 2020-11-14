import discord
from discord.ext import commands


class Settings(commands.Cog):
    def __init__(self, bot):
        self.guild_id = 777155838849843200
        self.roles = {
            "Muted": bot.get_guild(self.guild_id).get_role(123345),
            "MemPlus": bot.get_guild(self.guild_id).get_role(123345),
            "MemPro" : bot.get_guild(self.guild_id).get_role(123345),
            "MemEd"  : bot.get_guild(self.guild_id).get_role(123345),
            "Genius" : bot.get_guild(self.guild_id).get_role(123345),
            "Mod"    : bot.get_guild(self.guild_id).get_role(123345)
        }
        self.logging_channel = 688126468517396588
        self.reports_channel = 688125770186489888
        self.permissions = Permissions(bot, self.guild_id, self.roles)


class Permissions:
    def __init__(self, bot, guild_id, roles):
        self.guild_id = guild_id
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
