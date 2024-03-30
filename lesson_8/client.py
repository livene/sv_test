from typing import Union, Optional

from starknet_py.contract import Contract
import starknet_py.cairo.felt
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner
from starknet_py.serialization import TupleDataclass
from starknet_py.net.gateway_client import GatewayClient

from data.models import TokenAmount, DEFAULT_TOKEN_ABI


class StarknetClient:
    chain_id = StarknetChainId.MAINNET

    def __init__(self, private_key: int, account_address: int):
        self.key_pair = KeyPair.from_private_key(private_key)
        self.signer = StarkCurveSigner(account_address, self.key_pair, StarknetClient.chain_id)
        # self.starknet_client = FullNodeClient(node_url=StarknetClient.node_url)
        self.starknet_client = GatewayClient(net="mainnet")
        self.account = Account(
            address=account_address,
            client=self.starknet_client,
            key_pair=self.key_pair,
            chain=StarknetChainId.MAINNET
        )

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
