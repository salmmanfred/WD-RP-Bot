from discord.ext.commands import Command


class Context(object):
    def __init__(self, bot, *args, **kwargs):
        self.bot = bot
        self.args = args
        self.kwargs = kwargs


class TestBot(object):
    def __init__(self, owner_ids=(298148752315777026, 529676139837521920)):
        self.owner_ids = list(owner_ids)
        self.commands = {}

    def add_command(self, cmd: Command):
        self.commands[cmd.name] = cmd
        for alias in cmd.aliases:
            self.commands[alias] = cmd

    def get_command(self, key) -> Command:
        return self.commands[key]

    def run_command(self, key, *args, **kwargs):
        cmd = self.get_command(key)
        cmd.invoke(Context(self, *args, **kwargs))
