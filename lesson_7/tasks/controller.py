from py_eth_async.client import Client
from py_eth_async.data.models import Networks
from py_eth_async.exceptions import HTTPException

from tasks.base import Base


class Controller(Base):
    def __init__(self, client: Client):
        super().__init__(client=client)
