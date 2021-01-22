import logging
from typing import List

from sqlalchemy import orm
import sqlalchemy
from . import Session
from . import Base
from . import Account
from .inventory import InventoryObject
from . import ShopEntry
logger = logging.getLogger(__name__)


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
        return self._get_session().query(Account).filter_by(id=id).one_or_none()

    def open_account(self, user) -> Account:
        if self.has_account(user.id):
            return self.get_account(user.id)
        logger.info(f"opening account {user.mention}")
        acc = Account.from_user(user)
        self._get_session().add(acc)
        logger.info(f"opened account {user.mention}")
        return acc

    def get_shop_entries(self, **filters) -> List[ShopEntry]:
        return self._get_session().query(ShopEntry).filter_by(**filters).all()

    def get_shop_entry(self, **filters):
        """
        :param filters: the filters to apply to the query
        :return: the first entry that matches your query
        """
        return self.get_shop_entries(**filters)[0]

    def add_shop_entry(self, name, value, emoji_id, uuid=None):
        entry = ShopEntry(name=name, value=value, emoji_id=emoji_id, uuid=uuid)
        self._get_session().add(entry)
        return entry
