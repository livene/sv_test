from typing import Union, Optional
from aiohttp.client_exceptions import ClientHttpProxyError
from aiohttp import ClientSession
from aiohttp_proxy import ProxyConnector
from loguru import logger
import random
from starknet_py.net.client_models import ContractClass, SierraContractClass

from starknet_py.contract import Contract
from starknet_py.net.client_errors import ClientError
from starknet_py.net.networks import MAINNET
import starknet_py.cairo.felt
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner
from starknet_py.serialization import TupleDataclass
from starknet_py.net.gateway_client import GatewayClient
from data import config

from data.models import TokenAmount, DEFAULT_TOKEN_ABI


class StarknetClient:
    chain_id = StarknetChainId.MAINNET

    def __init__(self, private_key: int, account_address: int, proxy: str = ''):
        self.hex_address = self.value_to_hex(account_address)
        self.key_pair = KeyPair.from_private_key(private_key)
        self.signer = StarkCurveSigner(account_address, self.key_pair, StarknetClient.chain_id)
        self.proxy = StarknetClient.normalize_proxy(proxy=proxy)

        self.connector = None
        self.session = None
        self.starknet_client = None
        self.account = None
        self.cairo_version = None

        if self.proxy:
            self.connector = ProxyConnector.from_url(self.proxy)
            self.session = ClientSession(connector=self.connector)
            # self.starknet_client = GatewayClient(
            #     net=MAINNET,
            #     session=self.session,
            # )
            self.starknet_client = FullNodeClient(
                node_url='https://starknet-mainnet.public.blastapi.io',
                session=self.session
            )
        else:
            logger.warning(f'Proxy not used')
            # alchemy, blastapi
            self.starknet_client = FullNodeClient(node_url=random.choice(config.NODE_URLS))

        self.account = Account(
            address=account_address,
            client=self.starknet_client,
            key_pair=self.key_pair,
            chain=StarknetClient.chain_id
        )

    async def __aenter__(self):
        self.cairo_version = await self.get_cairo_version()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.proxy:
            await self.session.close()

    async def get_decimals(self, token_address: int) -> int:
        contract = Contract(
            address=token_address,
            abi=DEFAULT_TOKEN_ABI,
            provider=self.account
        )
        return int(StarknetClient.get_data(
            await contract.functions['decimals'].call()
        ))

    async def get_balance(self, token_address: int) -> TokenAmount:
        return TokenAmount(
            amount=await self.account.get_balance(token_address=token_address, chain_id=StarknetChainId.MAINNET),
            decimals=await self.get_decimals(token_address=token_address),
            wei=True
        )

    def value_to_hex(self, value=None) -> Optional[str]:
        if not value:
            return '0x{:064x}'.format(self.account.address)
        return '0x{:064x}'.format(value)

    @staticmethod
    def normalize_proxy(proxy: str = ''):
        if proxy and 'http' not in proxy:
            proxy = f'http://{proxy}'
        return proxy

    @staticmethod
    def get_data(info: Union[int, TupleDataclass, tuple, dict]):
        if isinstance(info, int) or isinstance(info, str):
            return info
        elif isinstance(info, TupleDataclass):
            return info.as_tuple()[0]
        elif isinstance(info, tuple):
            return info[0]
        elif isinstance(info, dict):
            return list(info.values())[0]
        return info

    @staticmethod
    def get_text_from_decimal(info: Union[int, TupleDataclass, tuple, dict]) -> Optional[str]:
        info = int(StarknetClient.get_data(info))
        if isinstance(info, str) and info.isdigit():
            info = int(info)
        return str(starknet_py.cairo.felt.decode_shortstring(info)).replace('\0', '').strip()

    async def get_my_ip(self):
        try:
            async with self.session.get("https://ipinfo.io/ip") as response:
                return await response.text()
        except ClientHttpProxyError:
            logger.error('Error occurred while using the proxy.')
            raise

    async def get_cairo_version(self):
        contract_class_hash = await self.starknet_client.get_class_hash_at(contract_address=self.account.address)
        contract_class = await self.starknet_client.get_class_by_hash(class_hash=contract_class_hash)
        return 1 if isinstance(contract_class, SierraContractClass) else 0
