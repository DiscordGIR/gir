import random
import math

from cogs.commands.hungergames.game import Game
from cogs.commands.hungergames.player import Player
from cogs.commands.hungergames.enums import ErrorCode

PLAYER_LIMIT = 24

class HungerGames:
    active_games = {}
    autoplay = False

    def new_game(self, channel_id, owner_id, owner_name, title):
        if channel_id in self.active_games:
            return ErrorCode.GAME_EXISTS
        self.active_games[channel_id] = Game(owner_name, owner_id, title)
        return True

    def add_player(self, channel_id, name, _id, volunteer=False):
        if channel_id not in self.active_games:
            return ErrorCode.NO_GAME
        this_game = self.active_games[channel_id]

        if this_game.has_started:
            return ErrorCode.GAME_STARTED
        if len(this_game.players) >= PLAYER_LIMIT:
            return ErrorCode.GAME_FULL

        district = math.ceil((len(this_game.players) + 1) / 2)
        p = Player(name, _id, district)
        if not this_game.add_player(p):
            return ErrorCode.PLAYER_EXISTS

        if volunteer:
            return f"**District {p.district} | {p.name}** volunteers as tribute!"
        return f"**District {p.district} | {p.name}** is selected to be a tribute!"

    def remove_player(self, channel_id, _id):
        if channel_id not in self.active_games:
            return ErrorCode.NO_GAME
        this_game = self.active_games[channel_id]

        if this_game.has_started:
            return ErrorCode.GAME_STARTED

        if not this_game.remove_player(_id):
            return ErrorCode.PLAYER_DOES_NOT_EXIST
        return f"Player <@{_id}> was removed from the game."

    def pad_players(self, channel_id, group):
        if channel_id not in self.active_games:
            return ErrorCode.NO_GAME
        this_game = self.active_games[channel_id]

        if this_game.has_started:
            return ErrorCode.GAME_STARTED
        if len(this_game.players) >= PLAYER_LIMIT:
            return ErrorCode.GAME_FULL
        if group is None:
            return ErrorCode.INVALID_GROUP

        new_players = random.sample(group, min(PLAYER_LIMIT - len(this_game.players), len(group)))
        messages = []
        for p in new_players:
            ret = self.add_player(channel_id,  p.display_name, p.id)
            if ret is not ErrorCode.PLAYER_EXISTS:
                messages.append(ret)

        if len(messages) == 0:
            return "No tributes were added."
        return "\n".join(messages)

    def status(self, channel_id):
        if channel_id not in self.active_games:
            return ErrorCode.NO_GAME
        this_game = self.active_games[channel_id]

        player_list = []
        for p in this_game.players_sorted:
            if p.alive:
                player_list.append(f"District {p.district}| {p.name}")
            else:
                player_list.append(f"~~District {p.district} | {p.name}~~")

        summary = {
            'title': this_game.title,
            'footer': f"Players: {len(this_game.players)}/{PLAYER_LIMIT} | Host: {this_game.owner_name}"
        }

        if len(player_list) == 0:
            summary['description'] = "No players have joined yet"
        else:
            summary['description'] = "The following tributes are currently in the game:\n\n" + "\n".join(player_list)
        return summary, this_game.players_sorted

    def start_game(self, channel_id, member_id):
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
        return {'title': f"{this_game.title} | The Reaping",
                'footer': f"Total Players: {len(this_game.players)} | Owner {this_game.owner_name}",
                'description': f"The Reaping has concluded! {this_game.owner_name}, you may now "
                               "proceed the simulation with !hg step."}, this_game.players_sorted

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
                'title': f"{this_game.title} | Winner",
                'color': 0xd0d645,
                'messages': [f"The winner is {summary['winner'].name} from District {summary['winner'].district}!"],
                'footer': None,
                'members':[ [summary['winner'].id]]
            }
        
        if summary.get('allDead') is not None:
            self.active_games.pop(channel_id)
            return {
                'title': f"{this_game.title} | Winner",
                'color': 0xd0d645,
                'description': "All the contestants have died!",
                'footer': None
            }

        # if summary['description'] is not None and len(summary['messages']) > 0:
        #     formatted_msg = "{0}\n\n> {1}".format(summary['description'], "\n> ".join(summary['messages']))
        # elif summary['description'] is not None:
        #     formatted_msg = summary['description']
        # else:
        #     formatted_msg = "> {0}".format("\n> ".join(summary['messages']))

        return {
            'title': summary['title'],
            'color': summary['color'],
            'description': summary['description'],
            'messages': summary['messages'],
            'footer': summary['footer'],
            'members': summary['members']
        }