import os

import discord
import mongoengine
from cogs.utils.tasks import Tasks
from data.case import Case
from data.cases import Cases
from data.filterword import FilterWord
from data.guild import Guild
from data.tag import Tag
from data.user import User
from data.giveaway import Giveaway
from discord.ext import commands


class Settings(commands.Cog):
    """This class is used to hold the state of the bot. It serves as the connection between the bot
    and the database. Information about the guild, users, cases, etc. can all be looked up from here,
    and additionally permissions can be calculated for a given user.

    Parameters
    ----------
    commands : commands.Cog
        Superclass
    """

    def __init__(self, bot: discord.Client):
        """Initializes the state of the bot, including the connection with the MongoDB database,
        and the task scheduler.

        Parameters
        ----------
        bot : discord.Client
            Instance of discord.Client, passed in when the Cog is initialized.
        """

        mongoengine.register_connection(alias="default", name="botty")
        self.tasks = None
        self.bot = bot
        self.guild_id = int(os.environ.get("BOTTY_MAINGUILD"))
        self.permissions = Permissions(self.bot, self)

        print("Loaded database")

    async def load_tasks(self):
        self.tasks = Tasks(self.bot)

    def guild(self) -> Guild:
        """Returns the state of the main guild from the database.

        Returns
        -------
        Guild
            The Guild document object that holds information about the main guild.
        """

        return Guild.objects(_id=self.guild_id).first()

    async def get_nsa_channel(self, id) -> dict:
        """Returns the state of the main guild from the database.

        Returns
        -------
        Guild
            The Guild document object that holds information about the main guild.
        """

        _map = self.guild().nsa_mapping
        if str(id) in _map:
            return _map[str(id)]
        return None

    async def add_nsa_channel(self, main_channel_id, channel_id, webhook_id) -> dict:
        """Returns the state of the main guild from the database.

        Returns
        -------
        Guild
            The Guild document object that holds information about the main guild.
        """

        g = self.guild()
        _map = g.nsa_mapping
        _map[str(main_channel_id)] = {
            "channel_id": channel_id,
            "webhook_id": webhook_id,
        }
        g.save()

    async def all_rero_mappings(self):
        g = self.guild()
        current = g.reaction_role_mapping
        return current

    async def add_rero_mapping(self, mapping):
        g = self.guild()
        current = g.reaction_role_mapping
        the_key = list(mapping.keys())[0]
        current[str(the_key)] = mapping[the_key]
        g.reaction_role_mapping = current
        g.save()

    async def append_rero_mapping(self, mapping):
        g = self.guild()
        current = g.reaction_role_mapping
        the_key = list(mapping.keys())[0]
        current[str(the_key)] = current[str(the_key)] | mapping[the_key]
        g.reaction_role_mapping = current
        g.save()

    async def get_rero_mapping(self, id):
        g = self.guild()
        if id in g.reaction_role_mapping:
            return g.reaction_role_mapping[id]
        else:
            return None

    async def delete_rero_mapping(self, id):
        g = self.guild()
        if str(id) in g.reaction_role_mapping.keys():
            g.reaction_role_mapping.pop(str(id))
            g.save()

    async def save_emoji_webhook(self, id):
        g = Guild.objects(_id=self.guild_id).first()
        g.emoji_logging_webhook = id
        g.save()

    async def leaderboard(self) -> list:
        return User.objects[0:130].only('_id', 'xp').order_by('-xp', '-_id').select_related()

    async def leaderboard_rank(self, xp):
        users = User.objects().only('_id', 'xp')
        overall = users().count()
        rank = users(xp__gte=xp).count()
        return (rank, overall)

    async def inc_caseid(self) -> None:
        """Increments Guild.case_id, which keeps track of the next available ID to
        use for a case.
        """

        Guild.objects(_id=self.guild_id).update_one(inc__case_id=1)

    async def inc_xp(self, id, xp):
        """Increments user xp.
        """

        await self.user(id)
        User.objects(_id=id).update_one(inc__xp=xp)
        u = User.objects(_id=id).first()
        return (u.xp, u.level)

    async def inc_level(self, id) -> None:
        """Increments user level.
        """

        await self.user(id)
        User.objects(_id=id).update_one(inc__level=1)

    async def add_case(self, _id: int, case: Case) -> None:
        """Cases holds all the cases for a particular user with id `_id` as an
        EmbeddedDocumentListField. This function appends a given case object to
        this list. If this user doesn't have any previous cases, we first add
        a new Cases document to the database.

        Parameters
        ----------
        _id : int
            ID of the user who we want to add the case to.
        case : Case
            The case we want to add to the user.
        """

        # ensure this user has a cases document before we try to append the new case
        await self.cases(_id)
        Cases.objects(_id=_id).update_one(push__cases=case)

    async def add_filtered_word(self, fw: FilterWord) -> None:
        Guild.objects(_id=self.guild_id).update_one(push__filter_words=fw)

    async def remove_filtered_word(self, word: str):
        return Guild.objects(_id=self.guild_id).update_one(pull__filter_words__word=FilterWord(word=word).word)

    async def update_filtered_word(self, word: FilterWord):
        return Guild.objects(_id=self.guild_id, filter_words__word=word.word).update_one(set__filter_words__S=word)
    
    async def add_tag(self, tag: Tag) -> None:
        Guild.objects(_id=self.guild_id).update_one(push__tags=tag)

    async def remove_tag(self, tag: str):
        return Guild.objects(_id=self.guild_id).update_one(pull__tags__name=Tag(name=tag).name)

    async def edit_tag(self, tag):
        return Guild.objects(_id=self.guild_id, tags__name=tag.name).update_one(set__tags__S=tag)

    async def get_tag(self, name: str):
        tag = Guild.objects.get(_id=self.guild_id).tags.filter(name=name).first()
        if tag is None:
            return
        tag.use_count += 1
        await self.edit_tag(tag)
        return tag

    async def add_whitelisted_guild(self, id: int):
        g = Guild.objects(_id=self.guild_id)
        g2 = g.first()
        if id not in g2.filter_excluded_guilds:
            g.update_one(push__filter_excluded_guilds=id)
            return True
        return False

    async def remove_whitelisted_guild(self, id: int):
        g = Guild.objects(_id=self.guild_id)
        g2 = g.first()
        if id in g2.filter_excluded_guilds:
            g.update_one(pull__filter_excluded_guilds=id)
            return True
        return False

    async def add_ignored_channel(self, id: int):
        g = Guild.objects(_id=self.guild_id)
        g2 = g.first()
        if id not in g2.filter_excluded_channels:
            g.update_one(push__filter_excluded_channels=id)
            return True
        return False

    async def remove_ignored_channel(self, id: int):
        g = Guild.objects(_id=self.guild_id)
        g2 = g.first()
        if id in g2.filter_excluded_channels:
            g.update_one(pull__filter_excluded_channels=id)
            return True
        return False

    async def inc_points(self, _id: int, points: int) -> None:
        """Increments the warnpoints by `points` of a user whose ID is given by `_id`.
        If the user doesn't have a User document in the database, first create that.

        Parameters
        ----------
        _id : int
            The user's ID to whom we want to add/remove points
        points : int
            The amount of points to increment the field by, can be negative to remove points
        """

        # first we ensure this user has a User document in the database before continuing
        await self.user(_id)
        User.objects(_id=_id).update_one(inc__warn_points=points)

    async def set_warn_kicked(self, _id: int) -> None:
        """Set the `was_warn_kicked` field in the User object of the user, whose ID is given by `_id`,
        to True. (this happens when a user reaches 400+ points for the first time and is kicked).
        If the user doesn't have a User document in the database, first create that.

        Parameters
        ----------
        _id : int
            The user's ID who we want to set `was_warn_kicked` for.
        """

        # first we ensure this user has a User document in the database before continuing
        await self.user(_id)
        User.objects(_id=_id).update_one(set__was_warn_kicked=True)

    async def get_case(self, _id: int, case_id: int) -> Case:
        """Get the case with ID `case_id`, which belongs to the punishee given by ID `_id`.
        If the user doesn't have a Cases document in the database, first create that.

        Parameters
        ----------
        _id : int
            The ID of the user who we want to look the case up for
        case_id : int
            The ID of the case we want to find

        Returns
        -------
        Case
            The Case object representing the case.
        """

        # first we ensure this user has a Cases document in the database before continuing
        await self.cases(_id)
        case = Cases.objects(_id=_id).first()
        return case

    async def user(self, id: int) -> User:
        """Look up the User document of a user, whose ID is given by `id`.
        If the user doesn't have a User document in the database, first create that.

        Parameters
        ----------
        id : int
            The ID of the user we want to look up

        Returns
        -------
        User
            The User document we found from the database.
        """

        user = User.objects(_id=id).first()
        # first we ensure this user has a User document in the database before continuing
        if not user:
            user = User()
            user._id = id
            user.save()
        return user
    
    async def transfer_profile(self, oldmember, newmember):
        u = await self.user(oldmember)
        u._id = newmember
        u.save()
        
        u2 = await self.user(oldmember)
        u2.xp = 0
        u2.level = 0
        u2.save()
        
        cases = await self.cases(oldmember)
        cases._id = newmember
        cases.save()
        
        cases2 = await self.cases(oldmember)
        cases2.cases = []
        cases2.save()
        
        return u, len(cases.cases)

    async def retrieve_birthdays(self, date):
        return User.objects(birthday=date)

    async def cases(self, id: int) -> Cases:
        """Return the Document representing the cases of a user, whose ID is given by `id`
        If the user doesn't have a Cases document in the database, first create that.

        Parameters
        ----------
        id : int
            The user whose cases we want to look up.

        Returns
        -------
        Cases
            [description]
        """

        cases = Cases.objects(_id=id).first()
        # first we ensure this user has a Cases document in the database before continuing
        if cases is None:
            cases = Cases()
            cases._id = id
            cases.save()
        return cases

    async def rundown(self, id: int) -> list:
        """Return the 3 most recent cases of a user, whose ID is given by `id`
        If the user doesn't have a Cases document in the database, first create that.

        Parameters
        ----------
        id : int
            The user whose cases we want to look up.

        Returns
        -------
        Cases
            [description]
        """

        cases = Cases.objects(_id=id).first()
        # first we ensure this user has a Cases document in the database before continuing
        if cases is None:
            cases = Cases()
            cases._id = id
            cases.save()
            return []

        cases = cases.cases
        cases = filter(lambda x: x._type != "UNMUTE", cases)
        cases = sorted(cases, key=lambda i: i['date'])
        cases.reverse()
        return cases[0:3]
    
    async def get_giveaway(self, _id: int) -> Giveaway:
        """
        Return the Document representing a giveaway, whose ID (message ID) is given by `id`
        If the giveaway doesn't exist in the database, then None is returned.

        Parameters
        ----------
        id : int
            The ID (message ID) of the giveaway
        
        Returns
        -------
        Giveaway
        """
        giveaway = Giveaway.objects(_id=_id).first()
        return giveaway
    
    async def add_giveaway(self, id: int, channel: int, name: str, entries: list, winners: int, ended: bool = False, prev_winners=[]) -> None:
        """
        Add a giveaway to the database.

        Parameters
        ----------
        id : int
            The message ID of the giveaway
        channel : int
            The channel ID that the giveaway is in
        name : str
            The name of the giveaway.
        entries : list
            A list of user IDs who have entered (reacted to) the giveaway.
        winners : int
            The amount of winners that will be selected at the end of the giveaway.
        """
        giveaway = Giveaway()
        giveaway._id = id
        giveaway.channel = channel
        giveaway.name = name
        giveaway.entries = entries
        giveaway.winners = winners
        giveaway.is_ended = ended
        giveaway.previous_winners = prev_winners
        giveaway.save()

    async def get_locked_channels(self):
        return self.guild().locked_channels

    async def add_locked_channels(self, channel):
        Guild.objects(_id=self.guild_id).update_one(push__locked_channels=channel)

    async def remove_locked_channels(self, channel):
        Guild.objects(_id=self.guild_id).update_one(pull__locked_channels=channel)

    async def add_raid_phrase(self, phrase: str) -> bool:
        existing = self.guild().raid_phrases.filter(word=phrase)
        if(len(existing) > 0):
            return False
        Guild.objects(_id=self.guild_id).update_one(push__raid_phrases=FilterWord(word=phrase, bypass=5, notify=True))
        return True
    
    async def remove_raid_phrase(self, phrase: str):
        Guild.objects(_id=self.guild_id).update_one(pull__raid_phrases__word=FilterWord(word=phrase).word)

    async def inc_trivia_points(self, _id, points):
        await self.user(_id)
        User.objects(_id=_id).update_one(inc__trivia_points=points)
        u = User.objects(_id=_id).first()
        return u.trivia_points

    async def reset_trivia_points(self):
        users = User.objects(trivia_points__ne=0, trivia_points__exists=True)
        count = users.count()
        if count > 0:
            for u in users:
                u.trivia_points = 0
                u.save()
        return count

    async def trivia_leaderboard(self) -> list:
        return User.objects[0:100].only('_id', 'trivia_points').order_by('-trivia_points', '-_trivia_points').select_related()

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

    def __init__(self, bot: discord.Client, settings: Settings):
        """Initialize Permissions.

        Parameters
        ----------
        bot : discord.Client
            Instance of Discord client to look up a user's roles, permissions, etc.
        settings : Settings
            State of the bot
        """

        self.bot = bot
        self.settings = settings
        guild_id = self.settings.guild_id
        the_guild = settings.guild()

        # This dict maps a permission level to a lambda function which, when given the right paramters,
        # will return True or False if a user has that permission level.
        self.permissions = {
            0: lambda x, y: True,

            1: (lambda guild, m: self.hasAtLeast(guild, m, 2) or (guild.id == guild_id
                and guild.get_role(the_guild.role_memberplus) in m.roles)),

            2: (lambda guild, m: self.hasAtLeast(guild, m, 3) or (guild.id == guild_id
                and guild.get_role(the_guild.role_memberpro) in m.roles)),

            3: (lambda guild, m: self.hasAtLeast(guild, m, 4) or (guild.id == guild_id
                and guild.get_role(the_guild.role_memberedition) in m.roles)),

            4: (lambda guild, m: self.hasAtLeast(guild, m, 5) or (guild.id == guild_id
                and guild.get_role(the_guild.role_genius) in m.roles)),

            5: (lambda guild, m: self.hasAtLeast(guild, m, 6) or (guild.id == guild_id
                and guild.get_role(the_guild.role_moderator) in m.roles)),

            6: (lambda guild, m: self.hasAtLeast(guild, m, 7) or (guild.id == guild_id
                and m.guild_permissions.manage_guild)),

            7: (lambda guild, m: self.hasAtLeast(guild, m, 9) or (guild.id == guild_id
                and m == guild.owner)),

            9: (lambda guild, m: guild.id == guild_id
                and m.id == bot.owner_id),

            10: (lambda guild, m: guild.id == guild_id
                 and m.id == bot.owner_id),
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


def setup(bot):
    bot.add_cog(Settings(bot))
