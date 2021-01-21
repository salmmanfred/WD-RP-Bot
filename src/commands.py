from typing import Coroutine
import discord
from discord.ext import commands
from discord.ext.commands import Context
from accounting import Server
import logging

_commands = []  # an array of command callables
_server = None
_ready = False
logger = logging.getLogger(__name__)


def get_server() -> Server:
    return _server


def register_commands(bot: commands.Bot, s: Server):
    global _server
    global _ready
    _server = s
    for i in _commands:
        bot.add_command(i)

    _ready = True


def _add_command(cmd: Coroutine):
    _commands.append(cmd)


@commands.command(name="balance")
async def _balance(ctx: Context, *args, **kwargs):
    raise NotImplementedError()


_add_command(_balance)
