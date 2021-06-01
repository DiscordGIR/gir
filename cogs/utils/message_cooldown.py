from discord.ext import commands

class BucketType(commands.BucketType):
    message = 8
    
    def get_key(self, tag):
        return tag
        
        
class MessageCooldown(commands.Cooldown):
    __slots__ = ('rate', 'per', 'type', '_window', '_tokens', '_last')

    def __init__(self, rate, per, type):
        self.rate = int(rate)
        self.per = float(per)
        self.type = type
        self._window = 0.0
        self._tokens = self.rate
        self._last = 0.0

        if not isinstance(self.type, BucketType):
            raise TypeError('Cooldown type must be a BucketType')
        
    def copy(self):
        return MessageCooldown(self.rate, self.per, self.type)


class MessageCooldownMapping(commands.CooldownMapping):
    def __init__(self, original):
        self._cache = {}
        self._cooldown = original
        
    @classmethod
    def from_cooldown(cls, rate, per, type):
        return cls(MessageCooldown(rate, per, type))
