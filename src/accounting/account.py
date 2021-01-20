from sqlalchemy.orm import relationship
from sqlalchemy import Column, BigInteger, DECIMAL, text, JSON
from uuid import uuid4
from . import Base
import logging
from discord import Client, User

logger = logging.getLogger(__name__)


class Account(Base):
    __tablename__ = 'accounts'
    id = Column(BigInteger, primary_key=True)
    balance = Column(DECIMAL(precision=2), server_default=text('0'))
    inventory = Column(JSON, server_default=text('{}'))  # I know its not the most efficient to query but it is the easiest to update
    user = None

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
        return cls(id=user.id)
