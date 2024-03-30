import asyncio
from loguru import logger

from py_eth_async.data.models import Networks, TokenAmount
from py_eth_async.client import Client

from tasks.stargate import Stargate
from private_data import private_key1
from tasks.woofi import WooFi
from tasks.coredao import CoredaoBridge
from tasks.uniswap import Uniswap
from tasks.testnetbridge import Testnetbridge


async def main():
    client = Client(private_key=private_key1, network=Networks.Arbitrum)
    coredao = CoredaoBridge(client=client)
    amount = TokenAmount(amount=0.01, decimals=18)
    res = await coredao.bridge_usdt_bsc_to_usdt_coredao(amount=amount, max_fee=0.2)
    print(res)

    uniswap = Uniswap(client=client)
    amount_geth = TokenAmount(amount=0.1)
    res = await uniswap.swap_eth_to_geth(amount_geth=amount_geth)
    print(res)

    testnetbridge = Testnetbridge(client=client)
    amount_geth = TokenAmount(amount=0.01)
    res = await testnetbridge.swap_geth(geth_amount=amount_geth)
    print(res)


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
