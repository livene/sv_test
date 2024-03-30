import asyncio

from client import StarknetClient
from data import config
from tasks.myswap import MySwap


async def main():
    starknet_client = StarknetClient(private_key=config.private_key, account_address=config.account_address)
    my_swap = MySwap(starknet_client=starknet_client)
    # await my_swap.swap_eth_to_token(token_out_name='DAI')
    # await my_swap.swap_token_to_eth(token_out_name='DAI')


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
