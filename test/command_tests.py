import sys
from decimal import Decimal
from os import path, remove
import unittest
import asyncio
from TestBot import TestBot, Member

sys.path.append(path.join(path.dirname(
    path.dirname(path.abspath(__file__))), 'src'))
from accounting import Server
from commands import register_commands


def create_test_bot_and_server():
    try:
        remove('./test.db')
    except FileNotFoundError:
        pass
    bot = TestBot()
    server = Server('sqlite:///test.db', bot)
    register_commands(bot, server)
    return bot, server


class CommandTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_loop = asyncio.get_event_loop()

    def run_coro(self, coro):
        self.event_loop.run_until_complete(coro)

    def test_balance(self):
        async def test_balance():
            bot, server = create_test_bot_and_server()
            me = Member(529676139837521920)
            out = await bot.run_command('balance', me, bot)
            self.assertIn('0', out[0]['embed'].to_dict()['description'])
            server.print_money(me.id, Decimal(100))
            out = await bot.run_command('balance', me, bot)
            self.assertIn('100', out[0]['embed'].to_dict()['description'])

        self.run_coro(test_balance())

    def test_print_money(self):
        async def test_print_money():
            bot, server = create_test_bot_and_server()
            me = Member(529676139837521920)
            acc = server.get_account(me.id)
            self.assertEqual(acc.balance, Decimal('0'))
            await bot.run_command('print-money', me, bot, '1000', f'<@{me.id}>')
            acc = server.get_account(me.id)
            self.assertEqual(acc.balance, Decimal('1000'))

        self.run_coro(test_print_money())

    def test_remove_funds(self):
        async def test_remove_funds():
            bot, server = create_test_bot_and_server()
            me = Member(529676139837521920)
            acc = server.get_account(me.id)
            server.print_money(acc, Decimal('1000'))
            self.assertEqual(acc.balance, Decimal('1000'))
            await bot.run_command('remove-funds', me, bot, '1000', f'<@{me.id}>')
            acc = server.get_account(me.id)
            self.assertEqual(acc.balance, Decimal('0'))
        self.run_coro(test_remove_funds())

    def test_transfer(self):
        async def test_transfer():
            bot, server = create_test_bot_and_server()
            me = Member(529676139837521920)
            other = Member(298148752315777026)
            acc = server.get_account(me.id)
            other_acc = server.get_account(other.id)
            server.print_money(acc, Decimal('1000'))
            self.assertEqual(acc.balance, Decimal('1000'))
            self.assertEqual(other_acc.balance, Decimal('0'))
            await bot.run_command('transfer', me, bot, '1000', f'<@{other.id}>')
            self.assertEqual(other_acc.balance, Decimal('1000'))
            self.assertEqual(acc.balance, Decimal('0'))
        self.run_coro(test_transfer())

if __name__ == '__main__':
    unittest.main()
