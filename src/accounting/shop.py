from . import Base
from sqlalchemy import Column, CHAR, text, TEXT, Unicode, types
from uuid import uuid4
from .inventory import ItemType


class ShopEntry(Base):
    __tablename__ = "shop"
    entry_id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid4()))
    value = Column(types.DECIMAL, server_default=text('0'))
    item = Column(types.Enum(ItemType))
    emoji = Column(Unicode(1))
    page = Column(TEXT)
    description = Column(TEXT, server_default="There is no description available for this entry")
