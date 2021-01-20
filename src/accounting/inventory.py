import logging
from collections import defaultdict
from . import Farm
logger = logging.getLogger(__name__)


class Inventory(object):
    """
    I was considering storing this as a table in the database then I started to think of updatability
    when this updates I'm probably going to need to store more "things" in a users inventory
    """
    def __init__(self, guns: int = None, has_vest: bool = None, farms=None, **kwargs):
        self.guns = guns if guns is not None else 0
        self.has_vest = has_vest if has_vest is not None else False
        self.farms = farms if farms is not None else []

    @classmethod
    def from_dict(cls, json):
        d = defaultdict(lambda: None)
        d.update(json)
        if d["farms"] is not None:
            d["farms"] = [Farm.from_dict(i) for i in d["farms"]]
        return cls(**d)
