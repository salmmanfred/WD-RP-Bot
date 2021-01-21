from typing import Coroutine
import discord
from discord.ext import commands
from discord.ext.commands import Context
from accounting import Server
import argparse

_commands = []  # an array of command callables
_server = None
_ready = False


def get_server() -> Server:
    return _server


async def do_ready(ctx: Context):
    raise NotImplementedError()


def register_commands(bot: commands.Bot, s: Server):
    global server
    global ready
    server = s
    for i in _commands:
        bot.add_command(i)

    ready = True


def _add_command(cmd: Coroutine):
    _commands.append(cmd)


@commands.command(name="balance")
async def _balance(ctx: Context, *args, **kwargs):
    raise NotImplementedError()

_add_command(_balance)

@commands.command(name="shop")
async def _shop(ctx: Context, *args, **kwargs):
    raise NotImplementedError()
_add_command(_shop)


