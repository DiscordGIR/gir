import random
import math

from cogs.commands.hungergames.game import Game
from cogs.commands.hungergames.player import Player
from cogs.commands.hungergames.enums import ErrorCode


class HungerGames:
    active_games = {}

    def new_game(self, channel_id, owner_id, owner_name, title):
        if channel_id in self.active_games:
            return ErrorCode.GAME_EXISTS
        self.active_games[channel_id] = Game(owner_name, owner_id, title)
        return True

    def add_player(self, channel_id, name, gender=None, volunteer=False):
        if channel_id not in self.active_games:
            return ErrorCode.NO_GAME
        this_game = self.active_games[channel_id]

        if this_game.has_started:
            return ErrorCode.GAME_STARTED
        if len(this_game.players) >= 24:
            return ErrorCode.GAME_FULL

        if gender is not None:
            if type(gender) is bool:
                is_male = gender
            elif gender.lower() == "-m":
                is_male = True
            elif gender.lower() == "-f":
                is_male = False
            else:
                is_male = random.choice([True, False])
        elif name.lower().startswith("-m "):
            is_male = True
            name = name[3:]
        elif name.lower().startswith("-f "):
            is_male = False
            name = name[3:]
        else:
            is_male = random.choice([True, False])

        if len(name) > 32:
            return ErrorCode.CHAR_LIMIT

        district = math.ceil((len(this_game.players) + 1) / 2)
        p = Player(name, district, is_male)
        if not this_game.add_player(p):
            return ErrorCode.PLAYER_EXISTS
        gender_symbol = "♂" if is_male else "♀"
        if volunteer:
            return "**District {0} {1} | {2}** volunteers as tribute!".format(p.district, gender_symbol, p.name)
        return "**District {0} {1} | {2}** is selected to be a tribute!".format(p.district, gender_symbol, p.name)

    def remove_player(self, channel_id, name):
        if channel_id not in self.active_games:
            return ErrorCode.NO_GAME
        this_game = self.active_games[channel_id]

        if this_game.has_started:
            return ErrorCode.GAME_STARTED

        if not this_game.remove_player(name):
            return ErrorCode.PLAYER_DOES_NOT_EXIST
        return "Player {0} was removed from the game.".format(name)

    def pad_players(self, channel_id, group):
        if channel_id not in self.active_games:
            return ErrorCode.NO_GAME
        this_game = self.active_games[channel_id]

        if this_game.has_started:
            return ErrorCode.GAME_STARTED
        if len(this_game.players) >= 24:
            return ErrorCode.GAME_FULL
        if group is None:
            return ErrorCode.INVALID_GROUP

        new_players = random.sample(group, min(24 - len(this_game.players), len(group)))
        messages = []
        for p in new_players:
            if type(p) is tuple:
                ret = self.add_player(channel_id, p[0], p[1])
            else:
                ret = self.add_player(channel_id, p, None)
            if ret is not ErrorCode.PLAYER_EXISTS:
                messages.append(ret)

        if len(messages) == 0:
            return "No tributes were added."
        return "{0}".format("\n".join(messages))

    def status(self, channel_id):
        if channel_id not in self.active_games:
            return ErrorCode.NO_GAME
        this_game = self.active_games[channel_id]

        player_list = []
        for p in this_game.players_sorted:
            gender_symbol = "♂" if p.is_male else "♀"
            if p.alive:
                player_list.append("District {0} {1} | {2}".format(p.district, gender_symbol, p.name))
            else:
                player_list.append("~~District {0} {1} | {2}~~".format(p.district, gender_symbol, p.name))

        summary = {
            'title': this_game.title,
            'footer': "Players: {0}/24 | Host: {1}"
                      .format(len(this_game.players), this_game.owner_name)
        }

        if len(player_list) == 0:
            summary['description'] = "No players have joined yet"
        else:
            summary['description'] = "The following tributes are currently in the game:\n\n" + "\n".join(player_list)
        return summary

    def start_game(self, channel_id, member_id, prefix):
        if channel_id not in self.active_games:
            return ErrorCode.NO_GAME
        this_game = self.active_games[channel_id]

        if member_id != this_game.owner_id:
            return ErrorCode.NOT_OWNER
        if this_game.has_started:
            return ErrorCode.GAME_STARTED
        if len(this_game.players) < 2:
            return ErrorCode.NOT_ENOUGH_PLAYERS

        this_game.start()
        player_list = []
        for p in this_game.players_sorted:
            gender_symbol = "♂" if p.is_male else "♀"
            player_list.append("District {0} {1} | {2}".format(p.district, gender_symbol, p.name))

        return {'title': "{0} | The Reaping".format(this_game.title),
                'footer': "Total Players: {0} | Owner {1}".format(len(this_game.players), this_game.owner_name),
                'description': "The Reaping has concluded! Here are the tributes:\n\n{0}\n\n{1}, you may now "
                               "proceed the simulation with `{2}step`.".format("\n".join(player_list),
                                                                               this_game.owner_name, prefix)}

    def end_game(self, channel_id, owner_id):
        if channel_id not in self.active_games:
            return ErrorCode.NO_GAME
        this_game = self.active_games[channel_id]
        if owner_id != this_game.owner_id:
            return ErrorCode.NOT_OWNER

        return self.active_games.pop(channel_id)

    def step(self, channel_id, member_id):
        # TODO: Let moderators also step
        # TODO: Allow for group skip override
        if channel_id not in self.active_games:
            return ErrorCode.NO_GAME
        this_game = self.active_games[channel_id]

        if member_id != this_game.owner_id:
            return ErrorCode.NOT_OWNER
        if not this_game.has_started:
            return ErrorCode.GAME_NOT_STARTED

        summary = this_game.step()

        if summary.get('winner') is not None:
            self.active_games.pop(channel_id)
            return {
                'title': "{0} | Winner".format(this_game.title),
                'color': 0xd0d645,
                'description': "The winner is {0} from District {1}!".format(summary['winner'], summary['district']),
                'footer': None
            }
        
        if summary.get('allDead') is not None:
            self.active_games.pop(channel_id)
            return {
                'title': "{0} | Winner".format(this_game.title),
                'color': 0xd0d645,
                'description': "All the contestants have died!",
                'footer': None
            }

        if summary['description'] is not None and len(summary['messages']) > 0:
            formatted_msg = "{0}\n\n> {1}".format(summary['description'], "\n> ".join(summary['messages']))
        elif summary['description'] is not None:
            formatted_msg = summary['description']
        else:
            formatted_msg = "> {0}".format("\n> ".join(summary['messages']))

        return {
            'title': summary['title'],
            'color': summary['color'],
            'description': formatted_msg,
            'footer': summary['footer']
        }
