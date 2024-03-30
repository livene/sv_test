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
    next_initial_action_time = Column(Integer)
    stargate_swaps = Column(Integer)
    coredao_swaps = Column(Integer)
    testnetbridge_swaps = Column(Integer)
    initial_completed = Column(Boolean)
    next_activity_action_time = Column(Integer)
    completed = Column(Boolean)

    def __init__(
            self,
            private_key: str,
            address: Optional[str],
            stargate_swaps: int,
            coredao_swaps: int,
            testnetbridge_swaps: int,
    ) -> None:
        self.private_key = private_key
        self.address = address
        self.next_initial_action_time = 0
        self.stargate_swaps = stargate_swaps
        self.coredao_swaps = coredao_swaps
        self.testnetbridge_swaps = testnetbridge_swaps
        self.initial_completed = False
        self.next_activity_action_time = 0
        self.completed = False
