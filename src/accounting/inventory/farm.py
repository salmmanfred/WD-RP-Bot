import logging
from .inventory_utils import InventoryType


logger = logging.getLogger(__name__)


class Farm(InventoryType):
    def __init__(self, returns, ticks_left=12, **kw):
        super().__init__(**kw)
        logger.debug("new farm object created")
        self.returns = returns
        self.ticks_left = ticks_left

    def __repr__(self):
        return f"<{self.__class__.__name__}(ticks_left={self.ticks_left})>"


class WheatFarm(Farm):
    def __init__(self, **kw):
        super().__init__(10, **kw)


class PotatoFarm(Farm):
    def __init__(self, **kw):
        super().__init__(60, **kw)


class BananaFarm(Farm):
    def __init__(self, **kw):
        super().__init__(100, **kw)
