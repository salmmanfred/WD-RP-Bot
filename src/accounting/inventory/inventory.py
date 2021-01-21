import logging
from sqlalchemy import Column, JSON, BigInteger, ForeignKey, text, INTEGER, Boolean, Table, CHAR, types
from . import Base
import sys, inspect
from uuid import uuid4
from enum import Enum

logger = logging.getLogger(__name__)


class ItemType(Enum):
    pass


class InventoryObject(Base):
    """
    An inventory class
    """
    __tablename__ = 'inventory_items'
    owner = Column(BigInteger, ForeignKey('accounts.id'))
    item_id = Column(CHAR(36), default=uuid4, primary_key=True)
    item_type = Column(types.Enum(ItemType))
    item_info = Column(JSON, server_default='{}')
