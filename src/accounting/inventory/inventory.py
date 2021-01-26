import logging
from sqlalchemy import Column, JSON, BigInteger, ForeignKey, INTEGER, types
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship
from . import Base
from enum import Enum
from .gun import Handgun, UZI, AK47, ShotGun, Rifle, HeavyAmmunition, NormalAmmo, ArmourPiercingAmmo, BulletProofVest
from .farm import WheatFarm, BananaFarm, PotatoFarm

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
    AK47 = 7

    """Armour types:"""
    BulletProofVest = 8

    """Farm types:"""
    WheatFarm = 9
    PotatoFarm = 10
    BananaFarm = 11


item_class_map = {
    ItemType.Ammunition: NormalAmmo,
    ItemType.HeavyAmmunition: HeavyAmmunition,
    ItemType.ArmourPiercingAmmo: ArmourPiercingAmmo,

    ItemType.Handgun: Handgun,
    ItemType.UZI: UZI,
    ItemType.Shotgun: ShotGun,
    ItemType.Rifle: Rifle,
    ItemType.AK47: AK47,

    ItemType.BulletProofVest: BulletProofVest,

    ItemType.WheatFarm: WheatFarm,
    ItemType.PotatoFarm: PotatoFarm,
    ItemType.BananaFarm: BananaFarm
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
    owner_acc = relationship("Account")

    def _create_item(self, args):
        item_class_map[self.item_type.value](**args)

    def get_items(self):
        # noinspection PyArgumentList
        return [self._create_item(i) for i in self.item_info]

    def add_item(self, item):
        logger.info(f"added {item} to <@{self.owner}>'s inventory")
        self.item_info.append(item.to_json())

    def remove_item(self, index=0):
        logger.info(f"Removed {self.item_info[index]} from <@{self.owner}>'s inventory")
        self.item_info.pop(index)

    def equip_item(self, index=0):
        logger.info(f"Equipped {self.item_info[index]} to <@{self.owner}>")
        self.owner_acc.equip(self._create_item(self.item_info[index]))

    def update_item(self, item):
        assert reversed_class_map[type(item)] == item_class_map[self.item_type.value]
        self.item_info = item.to_json()
