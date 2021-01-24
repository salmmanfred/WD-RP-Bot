from discord import RequestsWebhookAdapter, Webhook
from discord.ext import commands

import accounting
import discord
import logging
from datetime import datetime
from os import mkdir
import click
import json
from collections import defaultdict
import sys
from commands import register_commands

try:
    mkdir('./logs')
except FileExistsError:
    pass

fp = f'./logs/{datetime.now()}.log'.replace(' ', '-')

if sys.platform.lower() == 'win32':
    fp = fp.replace(':', '.')

fh = logging.FileHandler(fp)
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] : %(message)s')

ch.setFormatter(formatter)
fh.setFormatter(formatter)


class DiscordWebhookHandler(logging.Handler):
    _colour_map = {
        logging.DEBUG: discord.Colour.dark_green(),
        logging.WARN: discord.Colour.dark_orange(),
        logging.INFO: discord.Colour.green(),
        logging.CRITICAL: discord.Colour.dark_red(),
        logging.ERROR: discord.Colour.dark_red(),
        logging.FATAL: discord.Colour.dark_red(),
        logging.NOTSET: discord.Colour.blue()
    }

    def __init__(self, webhook_url, level=logging.NOTSET):
        """
        :param webhook_url: the url to send requests to
        :param level: the level to log at
        """
        super().__init__(level)
        self._webhook = Webhook.from_url(webhook_url, adapter=RequestsWebhookAdapter())

    def emit(self, record: logging.LogRecord):
        try:
            embed = discord.Embed(colour=self._colour_map[record.levelno])
        except KeyError:
            embed = discord.Embed(colour=self._colour_map[logging.NOTSET])

        embed.add_field(name=record.name, value=record.message, inline=False)
        self._webhook.send(embed=embed)


def add_logger(name=None):
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    log.addHandler(ch)
    log.addHandler(fh)
    return log


def read_config(fp):
    _default_config = defaultdict(lambda: None)
    try:
        _default_config.update(json.load(open(fp, "r")))
        return _default_config
    except Exception:
        logger.warning(f'{fp} is either malformed or non existent defaulting to the default configuration')

    return _default_config


def set_up_webhook(url, *loggers):
    wh = DiscordWebhookHandler(url)
    wh.setLevel(logging.INFO)
    for i in loggers:
        i.addHandler(wh)


@click.command()
@click.option('--fp', default='config.json', help='The config file path')
@click.option('--token', help='The token used to connect to the discord bot')
@click.option('--logging_url', help='the url to send logging webhook events to')
@click.option('--prefix', help='the prefix for the bot')
@click.option('--url', help='the url for the database')
def main(fp, **configs):
    c = read_config(fp)
    print(type(c))

    keys_to_delete = []
    for k in configs.keys():
        if configs[k] is None:
            keys_to_delete.append(k)

    for k in keys_to_delete:
        del configs[k]
    c.update(configs)
    url = c.get("logging_url", None)
    if url is not None:
        set_up_webhook(url, logger, al, cl)  # I don't want to log discord stuff to webhooks
    prefix = 'wd!' if c["prefix"] is None else c["prefix"]
    bot = commands.Bot(command_prefix=prefix, owner_ids=c.get("owner_ids", []))
    with accounting.Server(c["url"], bot) as server:
        register_commands(bot, server)
        bot.run(c["token"])


if __name__ == '__main__':
    al = add_logger(accounting.__name__)
    add_logger(discord.__name__)
    cl = add_logger(commands.__name__)
    logger = add_logger(__name__)
    logger.info('Started!')
    main()
