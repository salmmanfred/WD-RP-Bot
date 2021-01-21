import logging
from sqlalchemy import orm
import sqlalchemy
from . import Session
from . import Base

logger = logging.getLogger(__name__)


class Server(object):

    def __init__(self, url):
        logger.info("Starting the server!")
        logger.debug(f"connecting to the database at {url}")
        self.engine = sqlalchemy.create_engine(url)
        Session.configure(bind=self.engine)
        self.session = Session()
        logger.debug("Creating database tables")
        Base.metadata.create_all()
        logger.debug("Tables created successfully")
        logger.info("Server started successfully")

    def _get_session(self) -> orm.Session:
        return self.session
