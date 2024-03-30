import random
from loguru import logger

from py_eth_async.client import Client

from data.models import Settings
from data.config import IMPORT_PATH
from utils.files_utils import get_initial_data_from_csv_file
from db_api.database import db, get_wallet
from db_api.models import Wallet


class Import:
    @staticmethod
    def wallets() -> None:
        print(f'''Open and fill in the {IMPORT_PATH}.\n''')
        input(f'Then press Enter.')
        data = get_initial_data_from_csv_file(path=IMPORT_PATH)
        if data:
            settings = Settings()
            imported = []
            edited = []
            total = len(data)
            for wallet in data:
                try:
                    private_key = wallet.private_key
                    name = wallet.name
                    proxy = wallet.proxy
                    if not private_key:
                        print(f"You didn't specify one or more of the mandatory values: private_key!")
                        continue

                    if len(private_key) == 64 or private_key.startswith('0x') and len(private_key) == 66:
                        wallet_instance = get_wallet(private_key=private_key)

                        if wallet_instance and (
                                wallet_instance.name != wallet.name or wallet_instance.proxy != wallet.proxy):
                            wallet_instance.name = wallet.name
                            wallet_instance.proxy = wallet.proxy
                            db.commit()
                            edited.append(wallet_instance)

                        else:
                            client = Client(private_key=private_key)
                            address = client.account.address
                            stargate_swaps = random.randint(
                                settings.stargate_swaps.from_, settings.stargate_swaps.to_)
                            coredao_swaps = random.randint(
                                settings.coredao_swaps.from_, settings.coredao_swaps.to_)
                            testnetbridge_swaps = random.randint(
                                settings.testnetbridge_swaps.from_, settings.testnetbridge_swaps.to_)
                            wallet_instance = Wallet(
                                private_key=private_key,
                                address=address,
                                stargate_swaps=stargate_swaps,
                                coredao_swaps=coredao_swaps,
                                testnetbridge_swaps=testnetbridge_swaps,
                                name=name,
                                proxy=proxy
                            )
                            db.insert(wallet_instance)
                            imported.append(wallet_instance)

                except:
                    logger.exception('Import.wallets')
                    print(f'Failed to import wallet!')

            text = ''
            if imported:
                text += '\n--- Imported\nN\taddress\tstargate_swaps\tcoredao_swaps\ttestnetbridge_swaps'
                for i, wallet in enumerate(imported):
                    text += f'\n{i + 1}\t{wallet.address}\t{wallet.stargate_swaps}\t{wallet.coredao_swaps}\t{wallet.testnetbridge_swaps}'

                text += '\n'

            if edited:
                text += '\n--- Edited\nN\taddress\tstargate_swaps\tcoredao_swaps\ttestnetbridge_swaps'
                for i, wallet in enumerate(edited):
                    text += f'\n{i + 1}\t{wallet.address}\t{wallet.stargate_swaps}\t{wallet.coredao_swaps}\t{wallet.testnetbridge_swaps}'

                text += '\n'

            print(
                f'{text}\nDone! {len(imported)}/{total} wallets were imported, '
                f'name have been changed at {len(edited)}/{total}.'
            )

        else:
            print(f'There are no wallets on the file!')
