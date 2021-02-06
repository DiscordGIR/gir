from discord.ext import commands


class HungryContext(commands.Context):
    def reply(self, message):
        return self.send("{0} | {1}".format(self.author.mention, message))
