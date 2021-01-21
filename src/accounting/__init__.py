"""
This python package will contain all of the information needed to simulate the economy
"""

import logging
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
Base = declarative_base()
Session = sessionmaker()
from .server import Server
from .account import Account
from .inventory.inventory import Inventory



logging.getLogger(__name__).addHandler(logging.NullHandler())
