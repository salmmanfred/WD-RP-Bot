from enum import Enum
import logging
from .inventory import InventoryObject
from collections import defaultdict


logger = logging.getLogger(__name__)


class FarmType(Enum):
    def __init__(self, price, returns_per_tick, ticks):
        self.ticks = ticks
        self.returns_per_tick = returns_per_tick
        self.price = price

    WHEAT = (100, 10, 12)


class Farm(InventoryObject):
    def __init__(self, farm_type: FarmType, ticks_left):
        super().__init__(farm_type.name, farm_type.value)
        logger.debug("new farm object created")
        self.type = farm_type
        self.ticks_left = ticks_left

    def __repr__(self):
        return f"<Farm(type='{self.type.name}', ticks_left={self.ticks_left})>"

    @classmethod
    def from_dict(cls, d):
        return cls(FarmType[d["farm_type"]], d["ticks_left"])
