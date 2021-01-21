from enum import Enum
from .inventory import InventoryFlag, InventoryAttribute


class Gun(InventoryFlag, Enum):
    pass


class Ammunition(object):
    price = 100
    damage_modifier = 0


class ArmourPiercingAmmo(InventoryAttribute, Ammunition):
    __attributename__ = "armour_piercing_ammo"
    price = 1000
    damage_modifier = 1000


class HeavyAmmunition(InventoryAttribute, Ammunition):
    __attributename__ = "heavy_ammo"
    price = 500
    damage_modifier = 500


class NormalAmmunition(InventoryAttribute, Ammunition):
    __attributename__ = "normal_ammo"
    price = 100
    damage_modifier = 0


