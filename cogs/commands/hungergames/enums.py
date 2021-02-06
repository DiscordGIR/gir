from enum import Enum


class RoundType(Enum):
    BLOODBATH = 'bloodbath'
    DAY = 'day'
    NIGHT = 'night'
    FEAST = 'feast'
    ARENA = 'arena'
    FALLEN = 'fallen'


class ErrorCode(Enum):
    NO_GAME = 0x0
    GAME_EXISTS = 0x1
    GAME_STARTED = 0x2
    GAME_FULL = 0x3
    PLAYER_EXISTS = 0x4
    CHAR_LIMIT = 0x5
    NOT_OWNER = 0x6
    INVALID_GROUP = 0x7
    NOT_ENOUGH_PLAYERS = 0x8
    GAME_NOT_STARTED = 0x9
    PLAYER_DOES_NOT_EXIST = 0xA
