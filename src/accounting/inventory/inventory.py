from sqlalchemy import Column, JSON, BigInteger, ForeignKey, INTEGER, types
from sqlalchemy.ext.mutable import MutableList
from . import Base
from enum import Enum
from .gun import *
from .farm import *

logger = logging.getLogger(__name__)


class ItemType(Enum):
    """An enumeration of all the known item types mapped to there item id"""
    def __eq__(self, other):
        if isinstance(other, int):
            return self.value == other
        if isinstance(other, ItemType):
            return self.value == other.value

    def __hash__(self):
        return hash(self.value)

    """Ammo types:"""
    Ammunition = 0
    HeavyAmmunition = 1
    ArmourPiercingAmmo = 2

    """Gun types:"""
    Handgun = 3
    UZI = 4
    Shotgun = 5
    Rifle = 6

    """Farm types:"""
    WheatFarm = 7
    PotatoFarm = 8
    BananaFarm = 9


item_class_map = {
    ItemType.Ammunition.value: NormalAmmo,
    ItemType.HeavyAmmunition.value: HeavyAmmunition,
    ItemType.ArmourPiercingAmmo.value: ArmourPiercingAmmo,

    ItemType.Handgun.value: Handgun,
    ItemType.UZI.value: UZI,
    ItemType.Shotgun.value: ShotGun,
    ItemType.Rifle.value: Rifle,

    ItemType.WheatFarm.value: WheatFarm,
    ItemType.PotatoFarm.value: PotatoFarm,
    ItemType.BananaFarm.value: BananaFarm
}
reversed_class_map = dict([(v, k) for k, v in item_class_map.items()])


class InventoryEntry(Base):
    """
    An inventory class
    """
    __tablename__ = 'inventory_items'
    entry_id = Column(INTEGER, autoincrement=True, primary_key=True)
    owner = Column(BigInteger, ForeignKey('accounts.id'))
    item_type = Column(types.Enum(ItemType))
    item_info = Column(MutableList.as_mutable(JSON), server_default='[]')

    def get_items(self):
        # noinspection PyArgumentList
        return [item_class_map[self.item_type.value](**i) for i in self.item_info]

    def add_item(self, item):
        logger.info(f"added {item} to <@{self.owner}>'s inventory")
        self.item_info.append(item.to_json())

    def remove_item(self, index=0):
        self.item_info.pop(index)

    def update_item(self, item):
        assert reversed_class_map[type(item)] == item_class_map[self.item_type.value]
        self.item_info = item.to_json()
