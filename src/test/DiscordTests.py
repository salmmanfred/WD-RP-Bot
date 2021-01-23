import discord
from discord.ext.commands import Command

class TestDiscord(object):
    def __init__(self):
        self.cmds = {}

    def add_command(self, cmd: Command):
        self.cmds[cmd.name] = cmd

    def run_command(self, name, args):
        cmd = self.cmds[name]
        assert isinstance(cmd, Command)


