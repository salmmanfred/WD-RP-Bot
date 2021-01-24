from . import Base
from sqlalchemy import Column, INTEGER, BigInteger, types
from enum import Enum


class Permission(Enum):
    """An enumeration of all permission modules"""
    All = 0

    """Economic permissions"""
    Transfer = 1                # gives the ability to transfer funds
    PrintMoney = 2              # gives the ability to print money
    RemoveFunds = 4             # gives the ability to remove funds

    """Gun permissions"""
    Immortal = 5                # removes the ability to be killed

    ShootHandgun = 6            # gives the ability to shoot a handgun
    ShootUZI = 7                # gives the ability to shoot an UZI
    ShootShotgun = 8            # gives the ability to shoot a shotgun
    ShootAK47 = 9               # gives the ability to shoot an AK47
    ShootRifle = 10             # gives the ability to shoot a rifle

    UseNormalAmmo = 11          # gives the ability to use normal ammunition
    UseHeavyAmmo = 12           # gives the ability to use heavy ammunition
    UseArmourPiercingAmmo = 13  # gives the ability to use armour piercing ammunition

    """Store permissions"""
    BuyItem = 14                # gives the ability to buy an item from the store
    SellItem = 15               # gives the ability to sell an item to the store

    AddItem = 16                # gives the ability to add an item to the store
    RemoveItem = 18             # gives the ability to remove an item from the store

    """Permissions permissions"""
    GivePermissions = 19        # gives the ability to assign permissions to a role
    RemovePermissions = 20      # gives the ability to remove permissions from a role


"""Aliases: these are helper variables that reduce the load on the end user"""
Shoot = [Permission.ShootHandgun, Permission.ShootShotgun, Permission.ShootUZI, Permission.ShootAK47, Permission.ShootRifle]
UseAmmo = [Permission.UseNormalAmmo, Permission.UseHeavyAmmo, Permission.UseArmourPiercingAmmo]


class PermissionsMap(Base):
    """A table mapping discord role ids to permissions"""
    __tablename__ = 'permissions'

    entry = Column(INTEGER, autoincrement=True, primary_key=True)
    role = Column(BigInteger)
    permission = Column(types.Enum(Permission))
