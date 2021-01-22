from . import Base
from sqlalchemy import Column, CHAR, types, text, TEXT, Unicode
from uuid import uuid4


class ShopEntry(Base):
    __tablename__ = "shop"
    entry_id = Column(CHAR(36), primary_key=True, default=uuid4)
    value = Column(types.DECIMAL, server_default=text('0'))
    emoji = Column(Unicode)
    name = Column(TEXT)
