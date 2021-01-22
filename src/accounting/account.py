from sqlalchemy.orm import relationship
from sqlalchemy import Column, BigInteger, DECIMAL, text, JSON
from . import Base
from .inventory import InventoryObject
import logging
from discord import Client, User

logger = logging.getLogger(__name__)


class Account(Base):
    __tablename__ = 'accounts'
    id = Column(BigInteger, primary_key=True)
    balance = Column(DECIMAL(precision=2), server_default=text('0'))
    inventory = relationship(InventoryObject)
    user = None

    def __init__(self, user=None, **kwargs):
        self.user = user
        super().__init__(**kwargs)

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
