import logging
from sqlalchemy import orm
import sqlalchemy
from . import Session
from . import Base
from . import Account
from .inventory import InventoryObject

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
        self._get_session().commit()
        logger.info(f"opened account {user.mention}")
        return acc
