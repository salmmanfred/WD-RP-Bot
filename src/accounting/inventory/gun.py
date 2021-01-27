from .inventory_utils import InventoryType
from time import time


class BulletProofVest(InventoryType):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.health_modifier = 1000


class Ammunition(InventoryType):
    def __init__(self, value, damage_modifier, **kwargs):
        super().__init__(**kwargs)
        self.value = value
        self.damage_modifier = damage_modifier

    def __repr__(self):
        return f"<{self.__class__.__name__}()>"


class ArmourPiercingAmmo(Ammunition):
    def __init__(self, **kwargs):
        super().__init__(750, 1000, **kwargs)


class HeavyAmmunition(Ammunition):
    def __init__(self, **kwargs):
        super().__init__(500, 500, **kwargs)


class NormalAmmo(Ammunition):
    def __init__(self, **kwargs):
        super().__init__(100, 0, **kwargs)


class Gun(InventoryType):

    def __init__(self, value, cooldown, damage, available_at=0, **kw):
        super().__init__(**kw)
        self.value = value
        self.cooldown = cooldown
        self.damage = damage
        self.available_at = available_at

    def __repr__(self):
        return f"<{self.__class__.__name__}(available_at={self.available_at})>"

    def to_json(self):
        super_json = super().to_json()
        super_json.update({
            "available_at": self.available_at
            # the only varying data is when the gun can be shot so its all we need to give
        })
        return super_json

    def can_shoot(self):
        return self.available_at >= time()


class Handgun(Gun):
    def __init__(self, **kw):
        super().__init__(100, 300, 500, **kw)


class UZI(Gun):
    def __init__(self, **kw):
        super().__init__(100, 150, 250, **kw)


class AK47(Gun):
    def __init__(self, **kw):
        super().__init__(1000, 100, 500, **kw)


class ShotGun(Gun):
    def __init__(self, **kw):
        super().__init__(1000, 400, 1000, **kw)


class Rifle(Gun):
    def __init__(self, **kw):
        super().__init__(1000, 600, 1500, **kw)
