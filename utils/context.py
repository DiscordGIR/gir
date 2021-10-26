from discord.commands import context

class GIRContext(context.ApplicationContext):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.whisper = False
