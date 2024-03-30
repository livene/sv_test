from typing import Optional
from pretty_utils.type_functions.classes import AutoRepr

from sqlalchemy import Column, Integer, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Wallet(Base, AutoRepr):
    __tablename__ = 'wallets'
    id = Column(Integer, primary_key=True)
    private_key = Column(Text, unique=True)
    address = Column(Text)
    name = Column(Text)
    proxy = Column(Text)
    next_initial_action_time = Column(Integer)
    swaps = Column(Integer)
    initial_completed = Column(Boolean)
    next_activity_action_time = Column(Integer)
    completed = Column(Boolean)

    def __init__(
            self,
            private_key: str,
            address: Optional[str],
            swaps: int,
            name: str = '',
            proxy: str = ''
    ) -> None:
        self.private_key = private_key
        self.address = address
        self.name = name
        self.proxy = proxy
        self.next_initial_action_time = 0
        self.swaps = swaps
        self.initial_completed = False
        self.next_activity_action_time = 0
        self.completed = False
