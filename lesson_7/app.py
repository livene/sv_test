import asyncio
from loguru import logger

from functions.create_files import create_files
from functions.Import import Import
from data import config

from functions.initial import initial
from functions.activity import activity


async def test():
    from db_api.database import get_wallets
    from py_eth_async.client import Client
    from data.models import zkSync
    from tasks.base import Base
    from tasks.mute import Mute
    from tasks.space_fi import SpaceFi
    from tasks.syncswap import SyncSwap

    wallet = get_wallets()[0]

    client = Client(private_key=wallet.private_key, network=zkSync)

    base = Base(client=client)

    # await base.get_token_info(contract_address='0x80115c708e12edd42e504c1cd52aea96c547c05c')
    # Base.parse_params('0x2cc4081e00000000000000000000000000000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000179fd40000000000000000000000000000000000000000000000000000000064ff7bf1000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000060000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000038d7ea4c680000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000002000000000000000000000000080115c708e12edd42e504c1cd52aea96c547c05c00000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000600000000000000000000000005aea5775959fbc2557cc8789bc1bf90a239d9a91000000000000000000000000e747990d5a3df6737851022cba3a32efe85684e700000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000')

    mute = Mute(client=client)
    # print(await mute.swap_eth_to_usdc())
    # print(await mute.swap_usdc_to_eth())

    space_fi = SpaceFi(client=client)
    # print(await space_fi.swap_eth_to_usdc())

    sync_swap = SyncSwap(client=client)
    print(await sync_swap.swap_eth_to_usdc())


async def start_script():
    await asyncio.wait([
        asyncio.create_task(initial()),
        asyncio.create_task(activity()),
    ])


async def start_okx_withdraw():
    pass


if __name__ == '__main__':
    create_files()
    print(f'''Select the action:
1) Import wallets from the {config.IMPORT_PATH} to the DB;
2) OKX Withdraw 
3) Start the script;
4) Exit.''')

    try:
        # loop = asyncio.get_event_loop()
        loop = asyncio.new_event_loop()
        action = int(input('> '))
        if action == 1:
            Import.wallets()
        elif action == 2:
            loop.run_until_complete(start_okx_withdraw())
        elif action == 3:
            loop.run_until_complete(start_script())
        elif action == 4:
            loop.run_until_complete(test())
        else:
            exit(1)

    except KeyboardInterrupt:
        print()

    # except ValueError:
    #     print(f"You didn't enter a number!")

    except BaseException as e:
        logger.exception('main')
        print(f'\nSomething went wrong: {e}\n')
