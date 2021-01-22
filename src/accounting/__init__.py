"""
This python package will contain all of the information needed to simulate the economy
"""

import logging
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
Session = sessionmaker(autocommit=True)
from .account import Account
from .shop import ShopEntry
from .server import Server

logging.getLogger(__name__).addHandler(logging.NullHandler())
