import logging
from decimal import Decimal
from typing import List
from discord import User, Role
from sqlalchemy import orm
import sqlalchemy
from . import Session
from . import Base
from . import Account
from .permission import PermissionsMap, Permission
from .inventory.inventory import InventoryEntry, item_class_map, ItemType, reversed_class_map
from . import ShopEntry
from .configuration import Configuration
import asyncio
import time
from datetime import datetime

logger = logging.getLogger(__name__)


def _can_transfer(source: Account, amount: Decimal):
    return source.balance >= amount


class Server(object):

    def __init__(self, url, bot=None, spt=10):
        logger.info("Starting the server!")
        self._bot = bot
        logger.debug(f"connecting to the database at {url}")
        self.engine = sqlalchemy.create_engine(url)
        Session.configure(bind=self.engine)
        self.session = Session()
        logger.debug("Creating database tables")
        Base.metadata.create_all(self.engine)
        logger.debug("Tables created successfully")
        logger.info("Reading the config data")
        self.last_tick_timestamp = int(self._get_config_val("LAST_TICK_TIMESTAMP", int(
            datetime.combine(datetime.utcnow(), datetime.min.time()).timestamp())))
        asyncio.get_event_loop().create_task(self.tick_loop(spt))
        logger.info("Server started successfully")

    async def tick_loop(self, spt=10):
        while 1:
            await asyncio.sleep(spt)
            next_tick_timestamp = self.last_tick_timestamp + 24 * 60 * 60
            while next_tick_timestamp <= time.time():
                await self.clock(next_tick_timestamp)
                next_tick_timestamp = self.last_tick_timestamp + 24 * 60 * 60

    async def clock(self, timestamp):
        self.last_tick_timestamp = timestamp
        self._set_config_val("LAST_TICK_TIMESTAMP", self.last_tick_timestamp)
        # TODO: some clock related activities

    def _get_config_val(self, key, default=None):
        entry = self._get_session().query(Configuration).filter_by(key=key).one_or_none()
        if entry is None:
            entry = Configuration(key=key, value=str(default))
            self._get_session().add(entry)
            self._get_session().commit()
        return entry.value

    def _set_config_val(self, key, value):
        if self._get_config_val(key, default=value) != value:
            entry = self._get_session().query(Configuration).filter_by(key=key).one()
            entry.value = value
            self._get_session().commit()

    def _get_session(self) -> orm.Session:
        return self.session

    def _get_bot(self):
        return self._bot

    async def check_authorised(self, user, *permissions):
        perms = []
        for role in user.roles:
            perms += self.get_permissions(role)
        owner = await self._get_bot().is_owner(user)
        return all([(i in perms) for i in permissions]) or Permission.All in perms or owner

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        logger.info("Stopping the server")
        self._get_session().commit()
        self._get_session().close()
        logger.info("Stopped the server")

    def has_account(self, id) -> bool:
        amount = self._get_session().query(Account).filter_by(id=id).count()
        return amount != 0

    def get_account(self, id) -> Account:
        if isinstance(id, Account):
            return id
        acc = self._get_session().query(Account).filter_by(id=id).one_or_none()
        if acc is None:
            acc = self.open_account(id)
        return acc

    def open_account(self, user) -> Account:
        logger.info(f"opening account {user}")
        if isinstance(user, User):
            acc = Account.from_user(user)
        else:
            acc = Account(id=user)

        self._get_session().add(acc)
        self._get_session().commit()
        logger.info(f"opened account {acc.id}")
        return acc

    def get_shop_entries(self, **filters) -> List[ShopEntry]:
        """
        :param filters: the filters applied to the query
        :return: all the shop entries that match the filters
        """
        return self._get_session().query(ShopEntry).filter_by(**filters).all()

    def transfer_cash(self, source, destination, amount):
        """
        :param source: the source account to transfer from
        :param destination: the destination to transfer too
        :param amount: the amount th transfer
        :return:
        """
        source_acc = self.get_account(source)
        destination_acc = self.get_account(destination)

        if _can_transfer(source, amount):
            source_acc.balance -= amount
            destination_acc.balance += amount
            self._get_session().commit()
        else:
            raise ValueError("source does not have the required funds to make that transfer")

    def print_money(self, destination, amount):
        destination_acc = self.get_account(destination)
        destination_acc.balance += amount
        self._get_session().commit()

    def remove_funds(self, source, amount):
        source_acc = self.get_account(source)
        if _can_transfer(source_acc, amount):
            source_acc.balance -= amount
            self._get_session().commit()
        else:
            raise ValueError("source account does not have that much cash")

    def transfer_item(self, source, destination, type, index=None, amount=None):
        if index is not None and amount is not None:
            raise ValueError("both index and amount can't be specified")
        if index is None and amount is None:
            amount = 1
        source_acc = self.get_account(source)
        destination_acc = self.get_account(destination)
        source_entry = self.get_inventory_entry(source_acc, type)
        destination_entry = self.get_inventory_entry(destination_acc, type)
        items = source_entry.get_items()

        def transfer(index):
            if index >= len(items):
                raise KeyError("That entry does not exist")
            item = items[index]
            source_entry.remove_item(index)
            destination_entry.add_item(item)
            self._get_session().commit()

        if index is not None:
            transfer(index)

        if amount is not None:
            if amount > len(items):
                raise ValueError("The source account does not have enough items")
            for i in range(amount):
                transfer(0)

    @staticmethod
    def get_type(item):
        return ItemType(reversed_class_map[item])

    def get_inventory_entry(self, account, type):
        entry = self._get_session().query(InventoryEntry).filter_by(owner=account.id, item_type=type).one_or_none()
        if entry is None:
            entry = InventoryEntry(owner=account.id, item_type=type)
            self._get_session().add(entry)
            self._get_session().commit()
        return entry

    def give(self, user, item, amount=1):
        acc = self.get_account(user)
        entry = self.get_inventory_entry(acc, item)
        for i in range(amount):
            entry.add_item(item_class_map[item]())
        self._get_session().commit()

    def get_shop_entry(self, **filters):
        """
        gets the first shop entry with the filters
        :param filters: the filters to apply to the query
        :return: the first entry that matches your query
        """
        return self.get_shop_entries(**filters)[0]

    def add_shop_entry(self, item, value, emoji, **kwargs):
        """
        adds a shop entry with the given parameters
        :param item:
        :param value:
        :param emoji:
        :param description:
        :param uuid:
        :return the shop entry that you created:
        """
        item = ItemType[item] if isinstance(item, str) else item
        entry = ShopEntry(value=value, item=item, emoji=emoji, **kwargs)
        self._get_session().add(entry)
        self._get_session().commit()
        return entry

    def remove_shop_entry(self, **filters):
        """

        :param filters:
        :return:
        """
        self._get_session().query(ShopEntry).filter_by(**filters).delete()

    def get_permissions(self, role):
        id = role.id if isinstance(role, Role) else role
        perm_entries = self._get_session().query(PermissionsMap).filter_by(role=id).all()
        return [i.permission for i in perm_entries]

    def give_permissions(self, role, *permissions):
        id = role.id if isinstance(role, Role) else role
        for i in permissions:
            p = PermissionsMap(role=id, permission=i)
            self._get_session().add(p)
            self._get_session().commit()

    def remove_permissions(self, role, *permissions):
        id = role.id if isinstance(role, Role) else role
        for i in permissions:
            self._get_session().query(PermissionsMap).filter_by(role=id, permission=i).delete()
            self._get_session().commit()
