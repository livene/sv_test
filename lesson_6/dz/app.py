'''
1) добавить в класс Controller функцию count_stargate_swaps для подсчета всех старгейт транзакций из доступных сетей
2) добавить в функцию select_random_action логику для testnetbridge
    (если нет geth на балансе, нужно покупать geth через uniswap)
'''

import asyncio
from loguru import logger

from functions.create_files import create_files
from functions.Import import Import
from data import config

from functions.initial import initial
from functions.activity import activity


async def test():
    from db_api.database import get_wallets
    from tasks.controller import Controller
    from py_eth_async.client import Client
    from tasks.stargate import Stargate
    from py_eth_async.data.models import Networks
    from data.models import Contracts

    wallet = get_wallets()[0]

    client = Client(private_key=wallet.private_key, network=Networks.BSC)

    controller = Controller(client=client)
    # print(await controller.count_testnetbridge_swaps())
    # print(await controller.count_coredao_swaps())
    print(await controller.count_stargate_swaps())


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

    except ValueError:
        print(f"You didn't enter a number!")

    except BaseException as e:
        logger.exception('main')
        print(f'\nSomething went wrong: {e}\n')
