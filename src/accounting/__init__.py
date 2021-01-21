"""
This python package will contain all of the information needed to simulate the economy
"""

import logging
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .server import Server
from .account import Account
from .inventory.inventory import Inventory
from .farm import Farm
from .gun import Gun

Base = declarative_base()
Session = sessionmaker()

logging.getLogger(__name__).addHandler(logging.NullHandler())
