import logging
from sqlalchemy import Column, JSON, BigInteger, ForeignKey, text, INTEGER, Boolean
from . import Base
import sys, inspect

logger = logging.getLogger(__name__)


class InventoryObject(object):
    """
    Used to represent more complicated objects where each one needs to persist unique attributes about itself
    """
    __objectname__ = "object"
    __default__ = {}
    value = 0


class InventoryAttribute(object):
    __attributename__ = "attribute"
    __default__ = 0
    __default_generator__ = None


class InventoryFlag(object):
    __flagname__ = "flag"
    __default__ = False


class Inventory(Base):
    """
    An inventory class
    """
    __tablename__ = 'inventories'
    owner = Column(BigInteger, ForeignKey('accounts.id'), primary_key=True)
    _cls_map = {}
    for cls in InventoryAttribute.__subclasses__():
        # this probably could be improved
        __dict__[cls.__attributename__] = Column(INTEGER, server_default=text(str(cls.__default__)), default=cls.__default_generator__)
        _cls_map[cls.__attributename__] = cls

    for cls in InventoryFlag.__subclasses__():
        __dict__[cls.__flagname__] = Column(Boolean, server_default=text(str(cls.__default__)))
        _cls_map[cls.__flagname__] = cls

    for cls in InventoryObject.__subclasses__():
        __dict__[cls.__objectname__] = Column(JSON, server_default=text(str(cls.__default__)))
        _cls_map[cls.__objectname__] = cls

    def _get_reversed_map(self):
        return {v: k for k, v in self._cls_map}

    def __getitem__(self, key):
        if isinstance(key, InventoryAttribute):
            key = self._get_reversed_map()[key]
        return self.__dict__[key]
