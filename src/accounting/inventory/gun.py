from enum import Enum


class Gun(Enum):
    pass


class Ammunition(object):
    price = 100
    damage_modifier = 0


class ArmourPiercingAmmo(Ammunition):
    __attributename__ = "armour_piercing_ammo"
    price = 1000
    damage_modifier = 1000


class HeavyAmmunition(Ammunition):
    __attributename__ = "heavy_ammo"
    price = 500
    damage_modifier = 500


class NormalAmmunition(Ammunition):
    __attributename__ = "normal_ammo"
    price = 100
    damage_modifier = 0


