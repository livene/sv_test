import asyncio

from starknet_py.contract import Contract

from proxy_client import StarknetClient
from tasks.myswap import MySwap
from data.models import TokenAmount
from tasks.base import Base

from data import config, models


async def main():
    async with StarknetClient(
        private_key=config.private_key,
        account_address=config.account_address,
        proxy=config.proxy
    ) as client:
        '''
        # -----------------------------------------------------------------------------     account address
        print('account address int:', client.account.address)
        print('account address hex:', hex(client.account.address))

        # -----------------------------------------------------------------------------     block info
        print(await client.starknet_client.get_block(block_number=1))

        # -----------------------------------------------------------------------------     get_balance example
        print('eht_balance:', (await client.get_balance(token_address=models.ETH_ADDRESS)).Ether)
        print('dai_balance:', (await client.get_balance(token_address=models.DAI_ADDRESS)).Ether)

        # -----------------------------------------------------------------------------     call example
        usdc_contract = Contract(
            address=models.USDC_ADDRESS,
            abi=models.DEFAULT_TOKEN_ABI,
            provider=client.account
        )
        info = await usdc_contract.functions['decimals'].call()
        # print(info)
        # print(type(info))
        print('decimals:', StarknetClient.get_data(info))

        eth_contract = Contract(
            address=models.ETH_ADDRESS,
            abi=models.DEFAULT_TOKEN_ABI,
            provider=client.account,
        )

        # get symbol
        info = await eth_contract.functions['symbol'].call()
        # print(info)
        # print(type(info))
        print('symbol:', StarknetClient.get_text_from_decimal(info=info))
        # get decimals
        info = await eth_contract.functions['decimals'].call()
        print('decimals:', StarknetClient.get_data(info))
        '''

        # -----------------------------------------------------------------------------     send transaction example
        # transaction example: https://starkscan.co/tx/0x002bf5229598d98b4ef838f1f8e9b5009dbeb0d0e4c658bd8d46f396c76e04e1

        # my_swap = MySwap(starknet_client=client)
        # amount = TokenAmount(amount=0.001)
        # res = await my_swap.swap_eth_to_token(amount_in=amount, token_out_name='USDC')
        # print(res)

        base = Base(starknet_client=client)
        res = await base._get_txs(account_address='0x07ea0df9741d4740cde40d5c404088103557e29f4f73c54e32eef2b6243b09cf')
        print(res)


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
