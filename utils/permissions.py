from utils.config import cfg
import discord

class Permissions:
    """A way of calculating a user's permissions.
    Level 0 is everyone.
    Level 1 is people with Member+ role
    Level 2 is people with Member Pro role
    Level 3 is people with Member Edition role
    Level 4 is people with Genius role
    Level 5 is people with Moderator role
    Level 6 is Admins
    Level 7 is the Guild owner (Aaron)
    Level 9 and 10 is the bot owner

    """

    def __init__(self):
        """Initialize Permissions.

        Parameters
        ----------
        bot : discord.Client
            Instance of Discord client to look up a user's roles, permissions, etc.
        settings : Settings
            State of the bot
        """

        the_guild = cfg.guild()

        # This dict maps a permission level to a lambda function which, when given the right paramters,
        # will return True or False if a user has that permission level.
        self.permissions = {
            0: lambda x, y: True,

            1: (lambda guild, m: self.hasAtLeast(guild, m, 2) or (guild.id == cfg.guild_id
                and guild.get_role(the_guild.role_memberplus) in m.roles)),

            2: (lambda guild, m: self.hasAtLeast(guild, m, 3) or (guild.id == cfg.guild_id
                and guild.get_role(the_guild.role_memberpro) in m.roles)),

            3: (lambda guild, m: self.hasAtLeast(guild, m, 4) or (guild.id == cfg.guild_id
                and guild.get_role(the_guild.role_memberedition) in m.roles)),

            4: (lambda guild, m: self.hasAtLeast(guild, m, 5) or (guild.id == cfg.guild_id
                and guild.get_role(the_guild.role_genius) in m.roles)),

            5: (lambda guild, m: self.hasAtLeast(guild, m, 6) or (guild.id == cfg.guild_id
                and guild.get_role(the_guild.role_moderator) in m.roles)),

            6: (lambda guild, m: self.hasAtLeast(guild, m, 7) or (guild.id == cfg.guild_id
                and guild.get_role(the_guild.role_administrator) in m.roles)),

            7: (lambda guild, m: self.hasAtLeast(guild, m, 9) or (guild.id == cfg.guild_id
                and m == guild.owner)),

            9: (lambda guild, m: guild.id == cfg.guild_id
                and m.id == cfg.owner_id),

            10: (lambda guild, m: guild.id == cfg.guild_id
                 and m.id == cfg.owner_id),
        }

        self.permission_names = {
            0: "Everyone and up",
            1: "Member Plus and up",
            2: "Member Pros and up",
            3: "Member Editions and up",
            4: "Geniuses and up",
            5: "Moderators and up",
            6: "Administrators and up",
            7: "Guild owner (Aaron) and up",
            9: "Bot owner",
            10: "Bot owner",
        }

    def hasAtLeast(self, guild: discord.Guild, member: discord.Member, level: int) -> bool:
        """Checks whether a user given by `member` has at least the permission level `level`
        in guild `guild`. Using the `self.permissions` dict-lambda thing.

        Parameters
        ----------
        guild : discord.Guild
            The guild to check
        member : discord.Member
            The member whose permissions we're checking
        level : int
            The level we want to check if the user has

        Returns
        -------
        bool
            True if the user has that level, otherwise False.
        """

        return self.permissions[level](guild, member)

    def level_info(self, level: int) -> str:
        return self.permission_names[level]

permissions = Permissions()