from sqlalchemy import Column, VARCHAR
from . import Base


class Configuration(Base):
    """
    A configuration map of keys to values,
    please note this is not the most efficient way of implementing this its just the most adaptable solution
    I did consider using an Enum for the key as it would be much quicker to query but given the small amount of
    rows I think it is reasonable to use a VarChar simply because its easier.
    """
    __tablename__ = "configuration"
    key = Column(VARCHAR(), primary_key=True)
    value = Column(VARCHAR(), primary_key=True)
