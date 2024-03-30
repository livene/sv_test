'''
Arbitrum:
arbitrum -> avalanche (2.5): https://arbiscan.io/tx/0x3ad0c8aa2b5675c3f6fbfde5fb6c668c95a99179db0b9f107a6068c7bfe0071b
arbitrum -> polygon (2.5): https://arbiscan.io/tx/0xad55c727e33ded6bfca74417705cebb31d307430b1da8dc8a17b02225e5a462a
arbitrum -> optimism (0.76): https://arbiscan.io/tx/0x9c7f2b4a0a554f4c470b2815534c47e2189ed42a64ae5c050a75cf50fc1d1f2a

Polygon:
polygon -> arbitrum (1): https://polygonscan.com/tx/0xc14084044d5abccb11647c9f6a6b2fa68df4551b828326d345bf27e77d755e38
polygon -> avalanche (1): https://polygonscan.com/tx/0x432b5592bb9bfdce14845844bd09c3bed9fc6bb54311608142ca60469e819346

Avalanche:
avalanche -> arbitrum (1): https://snowtrace.io/tx/0x0d14541440bf7731070649f9447365b61f7760b3f8895f8fa544265869a76e3c
avalanche -> polygon (1): https://snowtrace.io/tx/0x4716dcfa604b5e11cc8c930ecef8f7f0c42f05bd31d1eb1401c84fe798af9395
avalanche -> bsc (2.5 USDT): https://snowtrace.io/tx/0x47d2cfa1d89b1656c83c5548e0b5fd17cc54ea8f4674b3f02d0c324546778d53

Optimism:
optimism -> arbitrum (0.75): https://optimistic.etherscan.io/tx/0x7278b546cd4025d0f8e8120e77ff1a2d43344cf450bbe15e4114f9eb426d167f

'''

import asyncio
import random
from typing import Optional
from web3.types import TxParams
from web3.contract import AsyncContract
from eth_typing import ChecksumAddress

from tasks.base import Base
from py_eth_async.client import Client
from py_eth_async.data.models import TxArgs, TokenAmount
from py_eth_async.data.models import Networks, Network
from pretty_utils.type_functions.floats import randfloat

from data.config import logger
from data.models import Contracts, Settings


class Stargate(Base):
    supported_networks = [Networks.Avalanche, Networks.Polygon, Networks.Optimism, Networks.Arbitrum]
    contract_data = {
        Networks.Arbitrum.name: {
            'usdc_contract': Contracts.ARBITRUM_USDC_e,
            'stargate_contract': Contracts.ARBITRUM_STARGATE,
            'stargate_chain_id': 110,
            'src_pool_id': 1,
            'dst_pool_id': 1,
        },
        Networks.Avalanche.name: {
            'usdc_contract': Contracts.AVALANCHE_USDC,
            'stargate_contract': Contracts.AVALANCHE_STARGATE,
            'stargate_chain_id': 106,
            'src_pool_id': 1,
            'dst_pool_id': 1,
        },
        Networks.Polygon.name: {
            'usdc_contract': Contracts.POLYGON_USDC,
            'stargate_contract': Contracts.POLYGON_STARGATE,
            'stargate_chain_id': 109,
            'src_pool_id': 1,
            'dst_pool_id': 1,
        },
        Networks.Optimism.name: {
            'usdc_contract': Contracts.OPTIMISM_USDC,
            'stargate_contract': Contracts.OPTIMISM_STARGATE,
            'stargate_chain_id': 111,
            'src_pool_id': 1,
            'dst_pool_id': 1,
        },
        Networks.BSC.name: {
            'stargate_chain_id': 102,
            'src_pool_id': 1,
            'dst_pool_id': 2,
        }
    }

    async def send_usdc(
            self,
            to_network: Network,
            amount: Optional[TokenAmount] = None,
            dest_fee: Optional[TokenAmount] = None,
            slippage: float = 0.5,
            max_fee: float = 1
    ):
        failed_text = f'Failed to send {self.client.network.name} USDC to {to_network.name} via Stargate'
        # try:
        if self.client.network.name == to_network.name:
            return f'{failed_text}: The same source network and destination network'

        usdc_contract = await self.client.contracts.default_token(
            contract_address=Stargate.contract_data[self.client.network.name]['usdc_contract'].address)
        stargate_contract = await self.client.contracts.get(
            contract_address=Stargate.contract_data[self.client.network.name]['stargate_contract'])

        if not amount:
            amount = await self.client.wallet.balance(token=usdc_contract.address)

        logger.info(
            f'{self.client.account.address} | Stargate | '
            f'send USDC from {self.client.network.name} to {to_network.name} | amount: {amount.Ether}')

        lz_tx_params = TxArgs(
            dstGasForCall=0,
            dstNativeAmount=dest_fee.Wei if dest_fee else 0,
            dstNativeAddr=self.client.account.address if dest_fee else '0x0000000000000000000000000000000000000001'
        )

        args = TxArgs(
            _dstChainId=Stargate.contract_data[to_network.name]['stargate_chain_id'],
            _srcPoolId=Stargate.contract_data[to_network.name]['src_pool_id'],
            _dstPoolId=Stargate.contract_data[to_network.name]['dst_pool_id'],
            _refundAddress=self.client.account.address,
            _amountLD=amount.Wei,
            _minAmountLD=int(amount.Wei * (100 - slippage) / 100),
            _lzTxParams=lz_tx_params.tuple(),
            _to=self.client.account.address,
            _payload='0x'
        )

        value = await self.get_value(
            router_contract=stargate_contract,
            to_network_name=to_network.name,
            lz_tx_params=lz_tx_params
        )
        if not value:
            return f'{failed_text} | can not get value ({self.client.network.name})'

        native_balance = await self.client.wallet.balance()
        if native_balance.Wei < value.Wei:
            return f'{failed_text}: To low native balance: balance: {native_balance.Ether}; value: {value.Ether}'

        token_price = await self.get_token_price(token=self.client.network.coin_symbol)
        dst_native_amount_dollar = 0
        if dest_fee:
            dest_native_token_price = await self.get_token_price(token=to_network.coin_symbol)
            dst_native_amount_dollar = float(dest_fee.Ether) * dest_native_token_price
        network_fee = float(value.Ether) * token_price
        if network_fee - dst_native_amount_dollar > max_fee:
            return f'{failed_text} | too high fee: {network_fee - dst_native_amount_dollar} ({self.client.network.name})'

        if await self.approve_interface(
                token_address=usdc_contract.address,
                spender=stargate_contract.address,
                amount=amount
        ):
            await asyncio.sleep(random.randint(5, 10))
        else:
            return f'{failed_text} | can not approve'

        tx_params = TxParams(
            to=stargate_contract.address,
            data=stargate_contract.encodeABI('swap', args=args.tuple()),
            value=value.Wei
        )

        tx = await self.client.transactions.sign_and_send(tx_params=tx_params)
        receipt = await tx.wait_for_receipt(client=self.client, timeout=300)
        if receipt:
            return f'{amount.Ether} USDC was send from {self.client.network.name} to {to_network.name} via Stargate: {tx.hash.hex()}'
        return f'{failed_text}!'

        # except Exception as e:
        #     return f'{failed_text}: {e}'

    async def get_value(self, router_contract: AsyncContract, to_network_name: str,
                        lz_tx_params: TxArgs) -> Optional[TokenAmount]:
        res = await router_contract.functions.quoteLayerZeroFee(
            Stargate.contract_data[to_network_name]['stargate_chain_id'],
            1,
            self.client.account.address,
            '0x',
            lz_tx_params.list()
        ).call()
        return TokenAmount(amount=res[0], wei=True)

    @staticmethod
    async def get_network_with_usdc(address: ChecksumAddress) -> Optional[Network]:
        result_network = None
        max_balance = TokenAmount(amount=0)
        for network in Stargate.supported_networks:
            client = Client(network=network)
            usdc_balance = await client.wallet.balance(
                token=Stargate.contract_data[network.name]['usdc_contract'], address=address)
            if float(usdc_balance.Ether) > float(max_balance.Ether):
                max_balance = usdc_balance
                result_network = network
        return result_network

    @staticmethod
    def get_dst_network(exclude_networks: list[Network]) -> Optional[Network]:
        try:
            return random.choice(list(
                filter(lambda network: network not in exclude_networks, Stargate.supported_networks)))
        except IndexError:
            return None

    async def action(self):
        failed_text = 'Failed stargate bridge'
        settings = Settings()

        src_network = await Stargate.get_network_with_usdc(address=self.client.account.address)
        self.client = Client(private_key=self.client.account.key, network=src_network, proxy=self.client.proxy)
        dst_network = Stargate.get_dst_network(exclude_networks=[src_network])
        if not dst_network:
            return f'{failed_text}: can not get dst_network'

        usdc_contract = await self.client.contracts.default_token(
            contract_address=Stargate.contract_data[self.client.network.name]['usdc_contract'].address)

        amount = TokenAmount(
            amount=randfloat(
                from_=settings.stargate_swaps_usdc_amount.from_,
                to_=settings.stargate_swaps_usdc_amount.to_,
                step=0.00001
            ),
            decimals=await self.get_decimals(contract_address=usdc_contract.address)
        )
        if not amount.Wei:
            amount = None

        return await self.send_usdc(
            to_network=dst_network,
            amount=amount,
            max_fee=settings.max_fee
        )
