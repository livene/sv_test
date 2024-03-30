'''
eth -> usdc (0.001): https://explorer.zksync.io/tx/0xac1acb194970bb3c796a8b06c5d21a365b8b6be7408babe4b8f3218e3af28f08
eth -> usdc (0.0015): https://explorer.zksync.io/tx/0x55cc113c631972e2b639cebe811a92b834179dbb0c5433625788a81cae523ffd
usdc -> eth: https://explorer.zksync.io/tx/0x9572a59bad67c172cc19b5d9e4159fca079ddf4d5aa44eaac46a3b0ff535d77d

сигнатуры: https://www.4byte.directory/
'''

from py_eth_async.data.models import Network, Networks, GWei, RawContract, DefaultABIs
import time
from web3.types import TxParams

from tasks.base import Base
from py_eth_async.data.models import Ether, TxArgs, TokenAmount
from pretty_utils.type_functions.floats import randfloat

from data.models import Settings, Contracts


SpaceFiABI = [
    {
        'constant': False,
        'inputs': [
            {'name': 'amountOut', 'type': 'uint256'},
            {'name': 'paths', 'type': 'address[]'},
            {'name': 'to', 'type': 'address'},
            {'name': 'deadline', 'type': 'uint256'},
        ],
        'name': 'swapEthToToken',
        'outputs': [],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function'
    }
]


class SpaceFi(Base):
    router = RawContract(
        address='0xbe7d1fd1f6748bbdefc4fbacafbb11c6fc506d1d',
        abi=SpaceFiABI
    )

    async def swap_eth_to_usdc(self) -> str:
        settings = Settings()
        slippage = 1

        to_token = Contracts.USDC

        to_token = await self.client.contracts.default_token(contract_address=to_token)
        to_token_name = await to_token.functions.symbol().call()

        failed_text = f'Failed swap ETH to {to_token_name} via SpaceFi'

        amount = Ether(randfloat(
            from_=settings.eth_amount_for_swap.from_,
            to_=settings.eth_amount_for_swap.to_,
            step=0.0000001
        ))
        contract = await self.client.contracts.get(contract_address=SpaceFi.router)

        eth_price = await self.get_token_price(token='ETH')
        amount_out_min = TokenAmount(
            amount=float(amount.Ether) * eth_price * (1 - slippage / 100),
            decimals=await self.get_decimals(contract_address=to_token.address)
        )

        params = TxArgs(
            amountOut=amount_out_min.Wei,
            paths=[Contracts.WETH.address, Contracts.USDC.address],
            to=self.client.account.address,
            deadline=int(time.time() + 20 * 60),
        )

        # tx_params = TxParams(
        #     to=contract.address,
        #     data=contract.encodeABI('swapEthToToken', args=params.tuple()),
        #     value=amount.Wei
        # )

        tx_params = TxParams(
            to=contract.address,
            data=f'0x7ff36ab5'
                 f'{hex(amount_out_min.Wei)[2:].zfill(64)}'
                 f'{"80".zfill(64)}'
                 f'{str(self.client.account.address)[2:].lower().zfill(64)}'
                 f'{hex(int(time.time() + 20 * 60))[2:].zfill(64)}'
                 f'{"2".zfill(64)}'
                 f'{Contracts.WETH.address[2:].zfill(64)}'
                 f'{Contracts.USDC.address[2:].zfill(64)}',
            value=amount.Wei
        )

        # self.parse_params(tx_params['data'])

        # tx_params = await self.client.transactions.auto_add_params(tx_params)
        # return (await self.client.transactions.estimate_gas(self.client.w3, tx_params)).Wei

        tx = await self.client.transactions.sign_and_send(tx_params=tx_params)
        receipt = await tx.wait_for_receipt(client=self.client, timeout=300)
        if receipt:
            return f'{amount.Ether} ETH was swapped to {to_token_name} via SpaceFi: {tx.hash.hex()}'
        return f'{failed_text}!'
