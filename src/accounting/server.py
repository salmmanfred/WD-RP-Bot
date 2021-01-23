import logging
from decimal import Decimal
from typing import List
from discord import User
from sqlalchemy import orm
import sqlalchemy
from . import Session
from . import Base
from . import Account
from .inventory.inventory import InventoryEntry, item_class_map, ItemType, reversed_class_map
from . import ShopEntry

logger = logging.getLogger(__name__)


def _can_transfer(source: Account, amount: Decimal):
    return source.balance >= amount


class Server(object):

    def __init__(self, url):
        logger.info("Starting the server!")
        logger.debug(f"connecting to the database at {url}")
        self.engine = sqlalchemy.create_engine(url)
        Session.configure(bind=self.engine)
        self.session = Session()
        logger.debug("Creating database tables")
        Base.metadata.create_all(self.engine)
        logger.debug("Tables created successfully")
        logger.info("Server started successfully")

    def _get_session(self) -> orm.Session:
        return self.session

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        logger.info("Stopping the server")
        self._get_session().flush()
        self._get_session().close()
        logger.info("Stopped the server")

    def has_account(self, id) -> bool:
        amount = self._get_session().query(Account).filter_by(id=id).count()
        return amount != 0

    def get_account(self, id) -> Account:
        if isinstance(id, User):
            return self.get_account(id.id)
        if isinstance(id, Account):
            return id
        return self._get_session().query(Account).filter_by(id=id).one_or_none()

    def open_account(self, user) -> Account:
        logger.info(f"opening account {user}")
        if isinstance(user, User):
            acc = Account.from_user(user)
        else:
            acc = Account(id=user)

        self._get_session().add(acc)
        logger.info(f"opened account {acc.id}")
        return acc

    def get_shop_entries(self, **filters) -> List[ShopEntry]:
        return self._get_session().query(ShopEntry).filter_by(**filters).all()

    def transfer_cash(self, source, destination, amount):
        source_acc = self.get_account(source)
        destination_acc = self.get_account(destination)

        if _can_transfer(source, amount):
            source_acc.balance -= amount
            destination_acc.balance -= amount

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
            self._get_session().flush()
        return entry

    def give(self, user, item, amount=1):
        acc = self.get_account(user)
        entry = self.get_inventory_entry(acc, item)
        for i in range(amount):
            entry.add_item(item_class_map[item]())
        self._get_session().flush()

    def get_shop_entry(self, **filters):
        """
        :param filters: the filters to apply to the query
        :return: the first entry that matches your query
        """
        return self.get_shop_entries(**filters)[0]

    def add_shop_entry(self, item, value, emoji, description="There is no description available for this entry", uuid=None):
        item = ItemType[item] if isinstance(item, str) else item
        entry = ShopEntry(value=value, item=item, emoji=emoji, entry_id=uuid, description=description)
        self._get_session().add(entry)
        self._get_session().flush()
        return entry
