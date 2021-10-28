from typing import List
from utils.permissions import permissions
from discord.commands.permissions import Permission


class SlashPerms:
    def memplus_and_up(self) -> List[Permission]:
        return permissions.calculate_permissions(1)

    def mempro_and_up(self) -> List[Permission]:
        return permissions.calculate_permissions(2)

    def memed_and_up(self) -> List[Permission]:
        return permissions.calculate_permissions(3)

    def genius_and_up(self) -> List[Permission]:
        return permissions.calculate_permissions(4)

    ####################
    # Staff Roles
    ####################

    # // TODO: fix
    # def submod_or_admin_and_up(self) -> List[Permission]:
    #   return permissions.calculate_permissions(6)

    # // TODO: fix
    # def genius_or_submod_and_up(self) -> List[Permission]:
    #     return permissions.calculate_permissions(4)

    def mod_and_up(self) -> List[Permission]:
        return permissions.calculate_permissions(5)

    def admin_and_up(self) -> List[Permission]:
        return permissions.calculate_permissions(6)

    ####################
    # Other
    ####################

    def guild_owner_and_up(self) -> List[Permission]:
        return permissions.calculate_permissions(7)

    def bot_owner_and_up(self) -> List[Permission]:
        return permissions.calculate_permissions(9)


slash_perms = SlashPerms()
