from sqlalchemy.orm import relationship
from sqlalchemy import Column, BigInteger, DECIMAL, text
from . import Base
from .inventory import InventoryEntry
import logging
from discord import Client, User

logger = logging.getLogger(__name__)


class Account(Base):
    __tablename__ = 'accounts'
    id = Column(BigInteger, primary_key=True)
    balance = Column(DECIMAL, server_default=text('0'))
    inventory = relationship(InventoryEntry)
    user = None

    def __init__(self, user=None, **kwargs):
        self.user = user
        super().__init__(**kwargs)

    def get_inventory(self):
        return {i.item_type: i.get_items() for i in self.inventory}

    async def get_user(self, bot: Client = None):
        self.user = bot.get_user(self.id)
        if self.user is not None:
            return self.user
        if bot is None:
            return None
        self.user = await bot.fetch_user(self.id)
        return self.user

    @classmethod
    def from_user(cls, user: User):
        return cls(user=user, id=user.id)
