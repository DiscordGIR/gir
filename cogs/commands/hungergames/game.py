import random
import math
from cogs.commands.hungergames.enums import RoundType
from cogs.commands.hungergames.events import events


class Game:
    def __init__(self, owner_name, owner_id, title: str):
        self.owner_name = owner_name
        self.owner_id = owner_id
        self.title = title
        self.has_started = False

        # Player data
        self.players = {}
        self.players_available_to_act = set()
        self.players_dead_today = []
        self.total_players_alive = 0

        # Round counting
        self.day = 1
        self.days_since_last_event = 0
        self.consecutive_rounds_without_deaths = 0

        # Round order control
        self.bloodbath_passed = False
        self.day_passed = False
        self.fallen_passed = False
        self.night_passed = False

    @property
    def players_sorted(self):
        l = list(self.players.values())
        l.sort()
        return l

    def add_player(self, new_player):
        if new_player.id in self.players:
            return False
        self.players[new_player.id] = new_player
        return True

    def remove_player(self, _id):
        if _id in self.players:
            del self.players[_id]
            return True
        return False

    def start(self):
        self.total_players_alive = len(self.players)
        self.has_started = True

    def step(self):
        if self.total_players_alive == 1:
            self.has_started = False
            for p in self.players.values():
                if p.alive is True:
                    return {'winner': p}
                
        if self.total_players_alive == 0:
            self.has_started = False
            return {'allDead': True}

        if self.night_passed:
            self.day += 1
            self.days_since_last_event += 1
            self.day_passed = False
            self.fallen_passed = False
            self.night_passed = False

        feast_chance = 100 * (math.pow(self.days_since_last_event, 2) / 55.0) + (9.0 / 55.0)
        fatality_factor = random.randint(2, 4) + self.consecutive_rounds_without_deaths

        if self.day == 1 and not self.bloodbath_passed:
            step_type = RoundType.BLOODBATH
            fatality_factor += 2
            self.bloodbath_passed = True
        elif not self.day_passed and random.randint(0, 100) < feast_chance:
            step_type = RoundType.FEAST
            self.days_since_last_event = 0
            fatality_factor += 2
        elif self.days_since_last_event > 0 and random.randint(1, 20) == 1:
            step_type = RoundType.ARENA
            self.days_since_last_event = 0
            fatality_factor += 1
        elif not self.day_passed:
            step_type = RoundType.DAY
            self.day_passed = True
        elif self.day_passed and not self.fallen_passed:
            step_type = RoundType.FALLEN
            self.fallen_passed = True
        else:
            step_type = RoundType.NIGHT
            self.night_passed = True

        self.players_available_to_act = {p for p in self.players.values() if p.alive is True}
        
        
        members = []
        event = None
        if step_type is RoundType.FALLEN:
            messages = []
            for p in self.players_dead_today:
                messages.append("{0} | District {1}".format(p, p.district))
                members.append(p.id)
        else:
            if step_type is RoundType.ARENA:
                event = events['arena'][random.randint(0, len(events['arena']) - 1)]
            else:
                event = events[step_type.value]
            dead_players_now = len(self.players) - self.total_players_alive
            messages, members = self.__generate_messages(fatality_factor, event)
            if len(self.players) - self.total_players_alive == dead_players_now:
                self.consecutive_rounds_without_deaths += 1
            else:
                self.consecutive_rounds_without_deaths = 0

        summary = {
            'day': self.day,
            'roundType': step_type.value,
            'members': members,
            'messages': messages,
            'footer': "Tributes Remaining: {0}/{1} | Host: {2}"
                      .format(self.total_players_alive, len(self.players), self.owner_name)
        }

        if step_type is RoundType.FALLEN:
            summary['members'] = [[member] for member in summary['members']]
            summary['title'] = "{0} | {1}".format(self.title, "Fallen Tributes {0}".format(self.day))
            if len(self.players_dead_today) > 1:
                summary['description'] = "{0} cannon shots can be heard in the distance.".format(
                    len(self.players_dead_today))
                self.players_dead_today.clear()
            elif len(self.players_dead_today) == 1:
                summary['description'] = "1 cannon shot can be heard in the distance."
                self.players_dead_today.clear()
            else:
                summary['description'] = "No cannon shots are heard."
            summary['color'] = 0xaaaaaa
        else:
            summary['title'] = "{0} | {1}".format(self.title, event['title'].format(self.day))
            summary['description'] = event['description']
            summary['color'] = event['color']

        return summary

    def __generate_messages(self, fatality_factor, event):
        messages = []
        members = []
        while len(self.players_available_to_act) > 0:
            members_sublist = []
            f = random.randint(0, 10)
            if f < fatality_factor and self.total_players_alive > 1:
                # time to die
                action = random.choice(event['fatal'])
                if action['killed'] is list and len(action['killed']) >= self.total_players_alive:
                    # must have one player remaining
                    continue
            else:
                # live to see another round
                action = random.choice(event['nonfatal'])

            tributes = action['tributes']
            if tributes > len(self.players_available_to_act):
                # not enough tributes for this action
                continue

            p = random.choice(tuple(self.players_available_to_act))
            self.players_available_to_act.remove(p)
            members_sublist.append(p.id)
            active_players = [p]

            extra_tributes = tributes - 1
            while extra_tributes > 0:
                p = random.choice(tuple(self.players_available_to_act))
                members_sublist.append(p.id)
                self.players_available_to_act.remove(p)
                active_players.append(p)
                extra_tributes -= 1

            msg = action['msg'].format(*active_players)

            if action.get('killed') is not None:
                if action.get('killer') is not None:
                    for kr in action['killer']:
                        active_players[kr].kills += len(action['killed'])
                for kd in action['killed']:
                    active_players[kd].alive = False
                    self.players_dead_today.append(active_players[kd])
                    self.total_players_alive -= 1
                    active_players[kd].cause_of_death = msg

            messages.append(msg)
            members.append(members_sublist)
        return messages, members
