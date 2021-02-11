from typing import Coroutine
from discord import Embed
import discord
from discord.ext import commands
from discord.ext.commands import Context, Bot
from accounting import Server, Permission
from accounting.inventory import ItemType
from datetime import datetime
import time
import logging
from economy import shop
from decimal import Decimal

_commands = []
_events = []
_cogs = []
_server = None
_bot = None
logger = logging.getLogger(__name__)


def _add_event(event: Coroutine):
    _events.append(event)


def _add_command(cmd: Coroutine):
    _commands.append(cmd)


def _add_cog(cog):
    _cogs.append(cog)


class CommandFailureCog(commands.Cog):
    """A cog that handles failed commands and sends a message in response"""

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        embed = Embed(colour=discord.Colour.red(), title="Command Failed",
                      description=str(error))
        await ctx.reply(embed=embed)


_add_cog(CommandFailureCog())


def get_server() -> Server:
    return _server


def get_bot() -> Bot:
    return _bot


def get_acc_from_mention(mention: str):
    return get_server().get_account(int("".join([i for i in mention if i.isdigit()])))


def register_commands(bot: commands.Bot, s: Server):
    global _server
    global _bot
    _bot = bot
    _server = s
    for i in _commands:
        bot.add_command(i)

    for i in _events:
        bot.event(i)

    for i in _cogs:
        bot.add_cog(i)


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
    bal = bal.normalize() if bal == 0 else bal
    embed = Embed(colour=ctx.author.colour, title="balance", description=f"your balance is {bal}")
    await ctx.reply(embed=embed)


_add_command(_balance)


@commands.command(name="print-money")
async def _print_money(ctx: Context, amount, destination):
    """
    prints <amount> to <destination>
    """
    if await handle_auth(ctx, Permission.PrintMoney):
        destination_acc = get_acc_from_mention(destination)
        get_server().print_money(destination_acc, Decimal(amount))
        await ctx.reply(embed=Embed(title='Done!', description='Money Printed!'))


_add_command(_print_money)


@commands.command(name="remove-funds")
async def _remove_funds(ctx: Context, amount, source):
    """
    removes <amount> from <source>
    """
    if await handle_auth(ctx, Permission.RemoveFunds):
        source_acc = get_acc_from_mention(source)
        get_server().remove_funds(source_acc, Decimal(amount))
        await ctx.reply(embed=Embed(title="Done!", description="Funds Removed!"))


_add_command(_remove_funds)


@commands.command(name="transfer")
async def _transfer(ctx: Context, amount, destination):
    """
    transfers <amount> to <destination>
    """
    if await handle_auth(ctx, Permission.Transfer):
        amount = Decimal(amount)
        assert amount > 0
        destination_acc = get_acc_from_mention(destination)
        source_acc = get_server().get_account(ctx.author.id)
        get_server().transfer_cash(source_acc, destination_acc, amount)
        await ctx.reply(embed=Embed(title="Done!", description="Money Transferred"))


_add_command(_transfer)


@commands.command(name="give")
async def _give(ctx: Context, type, amount, destination):
    """
    gives <destination> <amount> of <type>
    """
    if await handle_auth(ctx, Permission.Transfer):
        destination_acc = get_acc_from_mention(destination)
        source_acc = get_server().get_account(ctx.author.id)
        amount = int(amount)
        type = ItemType[type]

        get_server().transfer_item(source_acc, destination_acc, type, amount=amount)
        resp_embed = Embed(colour=ctx.author.colour, title="Done!", description="Transferred item!")
        await ctx.reply(embed=resp_embed)


_add_command(_give)


@commands.command(name="shoot")
async def _shoot(ctx: Context, gun_type, ammo_type, victim):
    """
    shoots <victim> with a gun of type <gun_type> and ammo of type <ammo_type>
    """
    raise NotImplementedError()


@commands.command(name="ping")
async def _ping(ctx: Context):
    """
    pings the bot
    """
    await ctx.reply(
        f'Pong! - took me {round((time.time() - datetime.timestamp(ctx.message.created_at)) * 1000, 2)}ms to send a response')


_add_command(_ping)


@commands.command(name="shop")
async def _shop(ctx: Context, page=None):
    """
    opens the shop menu on <page>
    """
    if await handle_auth(ctx, Permission.BuyItem):
        if page is None:
            await shop.shop_short(ctx)
        else:
            await shop.shop(ctx, get_server(), page)


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
async def _authorise(ctx: Context, role, auth: str):
    """
    gives <role>'s permission to do the actions associated with <auth>
    """
    if await handle_auth(ctx, Permission.GivePermissions):
        role, perm = parse_auth_cmd(ctx, role, auth)
        get_server().give_permissions(role, perm)
        embed = Embed(colour=ctx.author.colour, title="Authorised!",
                      description=f"{role.name} now has the permission {perm.name}")
        await ctx.reply(embed=embed)


_add_command(_authorise)


@commands.command(name="de-authorise", aliases=["deauthorise", "deauthorize", "de-authorize"])
async def _de_authorise(ctx: Context, role, auth: str):
    """
    removes <role>'s permission to do the actions associated with <auth>
    """
    if await handle_auth(ctx, Permission.RemovePermissions):
        role, perm = parse_auth_cmd(ctx, role, auth)
        get_server().remove_permissions(role, perm)
        embed = Embed(colour=ctx.author.colour, title="De-authorised",
                      description=f"{role.name} no longer has the permission {perm.name}")
        await ctx.reply(embed=embed)


_add_command(_de_authorise)


@commands.command(name="credits")
async def _credits(ctx: Context):
    """
    shows the credits
    """
    embed = Embed(colour=ctx.author.colour, title="Credits",
                  description="Credit goes to gamingdiamond982 and salmmanfred for developing this bot")
    await ctx.reply(embed=embed)


_add_command(_credits)


@commands.command(name="cc")
async def _clear_cache(ctx):
    """
    clears the shops cache
    """
    if await handle_auth(ctx, Permission.All):
        await shop.clear_cache(ctx)


_add_command(_clear_cache)


@commands.command(name="cache")
async def _get_cache(ctx):
    """
    returns the shops cache
    """
    if await handle_auth(ctx, Permission.All):
        await shop.cache(ctx)


_add_command(_get_cache)


@commands.command(name="inven", aliases=("inventory",))
async def _get_inven(ctx):
    """
    returns the contents of your inventory
    """
    embeds = discord.Embed(title="Inventory", description='"An inventory that will suit all your needs"',
                           color=0x00ff00)
    inventory = get_server().get_account(ctx.message.author.id).get_inventory()
    for i in inventory.keys():
        embeds.add_field(name=f"{i.name}s:", value="".join([f"{i}, " for i in inventory[i]]))

    await ctx.reply(embed=embeds)


_add_command(_get_inven)


async def on_reaction_add(reaction, user):
    await shop.buy(reaction, user, get_server(), get_bot())


_add_event(on_reaction_add)
