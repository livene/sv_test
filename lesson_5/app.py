import asyncio
from loguru import logger

from functions.create_files import create_files
from functions.Import import Import
from data import config


async def start_script():
    pass


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
        loop = asyncio.get_event_loop()
        action = int(input('> '))
        if action == 1:
            Import.wallets()
        elif action == 2:
            loop.run_until_complete(start_okx_withdraw())
        elif action == 3:
            loop.run_until_complete(start_script())
        else:
            exit(1)

    except KeyboardInterrupt:
        print()

    except ValueError:
        print(f"You didn't enter a number!")

    except BaseException as e:
        logger.exception('main')
        print(f'\nSomething went wrong: {e}\n')
