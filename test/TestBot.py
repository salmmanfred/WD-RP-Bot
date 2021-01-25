from discord.ext.commands import Command
from discord.colour import Colour


class Role:
    def __init__(self, id):
        self.id = id


class Member:
    def __init__(self, id, colour=Colour.green(), roles=()):
        self.id = id
        self.colour = colour
        self.roles = [Role(r) for r in roles]


class Context(object):
    def __init__(self, bot, author, *args, **kwargs):
        self.bot = bot
        self.args = args
        self.kwargs = kwargs
        self.author = author
        self.responses = []

    async def reply(self, **kwargs):
        self.responses.append(kwargs)


class TestBot(object):
    def __init__(self, owner_ids=(298148752315777026, 529676139837521920)):
        self.owner_ids = list(owner_ids)
        self.commands = {}
        self.events = {}

    def add_command(self, cmd: Command):
        self.commands[cmd.name] = cmd
        for alias in cmd.aliases:
            self.commands[alias] = cmd

    def event(self, coro):
        self.events[coro.__name__] = coro

    def get_command(self, key) -> Command:
        return self.commands[key]

    async def is_owner(self, user):
        return user.id in self.owner_ids

    async def run_command(self, key, *args, **kwargs):
        cmd = self.get_command(key)
        ctx = Context(self, *args, **kwargs)
        args = list(args)
        args.pop(0)
        args.pop(0)
        await cmd.callback(ctx, *args, **kwargs)
        return ctx.responses
