from typing import Coroutine
from discord import Embed
import discord
from discord.ext import commands
from discord.ext.commands import Context, Bot
from accounting import Server, Permission
from datetime import datetime
import time
import logging
from economy import shop

_commands = []  # an array of command callables
_events = []
_server = None
_bot = None
logger = logging.getLogger(__name__)


def get_server() -> Server:
    return _server


def get_bot() -> Bot:
    return _bot


def register_commands(bot: commands.Bot, s: Server):
    global _server
    global _bot
    _bot = bot
    _server = s
    for i in _commands:
        bot.add_command(i)

    for i in _events:
        bot.event(i)


def _add_event(event: Coroutine):
    _events.append(event)


def _add_command(cmd: Coroutine):
    _commands.append(cmd)


async def handle_auth(ctx: Context, *permissions, user=None):
    user = ctx.author if user is None else user
    if not await get_server().check_authorised(user, *permissions):
        embed = Embed(colour=ctx.author.colour, title="Unauthorised", description="You're not authorised to do that")
        await ctx.reply(embed=embed)
        return False
    return True


@commands.command(name="balance", aliases=["bal"])
async def _balance(ctx: Context, *args, **kwargs):
    bal = get_server().get_account(ctx.author.id).balance
    embed = Embed(colour=ctx.author.colour, title="balance", description=f"your balance is {bal}")
    await ctx.reply(embed=embed)


_add_command(_balance)


@commands.command(name="ping")
async def _ping(ctx: Context, *args, **kwargs):
    await ctx.reply(
        f'Pong! - took me {round((time.time() - datetime.timestamp(ctx.message.created_at)) * 1000, 2)}ms to send a response')


_add_command(_ping)


@commands.command(name="shop")
async def _shop(ctx: Context, *args, **kwargs):
    if await handle_auth(ctx, Permission.BuyItem):
        await shop.shop(ctx, get_server())


_add_command(_shop)


def parse_auth_cmd(ctx, role, auth):
    guild = ctx.guild
    msg = ctx.message
    if len(msg.role_mentions) == 1:
        role = msg.role_mentions[0]
    else:
        role = discord.utils.get(guild.roles, name=role)

    if auth.isdigit():
        perm = Permission(int(auth))
    else:
        perm = Permission[auth]
    return role, perm


@commands.command(name="authorise", aliases=["authorize"])
async def _authorise(ctx: Context, role, auth: str, *args, **kwargs):
    if await handle_auth(ctx, Permission.GivePermissions):
        role, perm = parse_auth_cmd(ctx, role, auth)
        get_server().give_permissions(role, perm)
        embed = Embed(colour=ctx.author.colour, title="Authorised!",
                      description=f"{role.name} now has the permission {perm.name}")
        await ctx.reply(embed=embed)


_add_command(_authorise)


@commands.command(name="de-authorise", aliases=["deauthorise", "deauthorize", "de-authorize"])
async def _de_authorise(ctx: Context, role, auth: str, *args, **kwargs):
    if await handle_auth(ctx, Permission.RemovePermissions):
        role, perm = parse_auth_cmd(ctx, role, auth)
        get_server().remove_permissions(role, perm)
        embed = Embed(colour=ctx.author.colour, title="De-authorised",
                      description=f"{role.name} no longer has the permission {perm.name}")
        await ctx.reply(embed=embed)


_add_command(_de_authorise)


@commands.command(name="credits")
async def _credits(ctx: Context, *args, **kwargs):
    embed = Embed(colour=ctx.author.colour, title="Credits",
                  description="Giving credit to the amazing devs of this bot")

    text = ""
    for i in get_bot().owner_ids:
        text += f"many thanks to <@{i}> for helping develop this bot,\n"

    embed.add_field(name="authors", value=text)

    await ctx.reply(embed=embed)


_add_command(_credits)


async def on_reaction_add(reaction, user):
    await shop.buy(reaction, user, get_server(), get_bot())


_add_event(on_reaction_add)


@commands.command(name="cc")
async def _clear_cache(ctx):
    if await handle_auth(ctx, Permission.All):
        await shop.clear_cache(ctx)


_add_command(_clear_cache)


@commands.command(name="inven")
async def _get_inven(ctx):
    if await handle_auth(ctx, Permission.All):
        embeds = discord.Embed(title="Inventory", description='"An inventory that will suit all your needs"', color=0x00ff00)
        s = " "
        for x in get_server().get_account(ctx.message.author.id).get_inventory():
            s = s + str(x) + "\n"
        embeds.add_field(name="Inventory", value=s, inline=False)

        await ctx.reply(embed=embeds)

_add_command(_get_inven)
