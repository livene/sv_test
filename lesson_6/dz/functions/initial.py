import asyncio
import random
import time
from typing import List
from loguru import logger

from py_eth_async.client import Client

from data.models import Settings
from functions.select_random_action import select_random_action
from tasks.controller import Controller
from db_api.database import db
from db_api.models import Wallet
from utils.utils import unix_to_strtime


def update_expired() -> None:
    now = int(time.time())
    expired_wallets: List[Wallet] = db.all(
        Wallet, Wallet.initial_completed.is_(False) & (Wallet.next_initial_action_time <= now)
    )
    if expired_wallets:
        settings = Settings()
        for wallet in expired_wallets:
            wallet.next_initial_action_time = now + random.randint(0, int(settings.initial_actions_delay.to_))
            logger.info(f'Action time was re-generated: {unix_to_strtime(wallet.next_initial_action_time)}.')

        db.commit()


async def initial() -> None:
    delay = 10
    now = int(time.time())
    settings = Settings()
    next_message_time = now + settings.initial_actions_delay.to_
    update_expired()
    while True:
        try:
            settings = Settings()
            now = int(time.time())
            wallet: Wallet = db.one(
                Wallet, Wallet.initial_completed.is_(False) & (Wallet.next_initial_action_time <= now)
            )
            if wallet:
                next_message_time = now + settings.initial_actions_delay.to_
                client = Client(private_key=wallet.private_key, proxy=wallet.proxy)
                controller = Controller(client=client)
                action = await select_random_action(controller=controller, wallet=wallet, initial=True)
                now = int(time.time())
                if action == 'Processed':
                    wallet.initial_completed = True
                    wallet.next_activity_action_time = now + random.randint(
                        settings.activity_actions_delay.from_, settings.activity_actions_delay.to_
                    )
                    logger.success(f'{client.account.address} | Initial actions completed!')
                elif action == 'Insufficient balance':
                    wallet.next_initial_action_time = now + random.randint(
                        int(settings.initial_actions_delay.from_ / 2), int(settings.initial_actions_delay.to_ / 2)
                    )
                    logger.error(f'{client.account.address} Insufficient balance!')
                else:
                    status = await action()
                    now = int(time.time())

                    if 'Failed' not in status:
                        wallet.next_initial_action_time = now + random.randint(
                            settings.initial_actions_delay.from_, settings.initial_actions_delay.to_
                        )
                        logger.success(status)
                    else:
                        wallet.next_initial_action_time = now + random.randint(5 * 60, 10 * 60)
                        logger.error(status)

                    try:
                        next_action_time = min((wallet.next_initial_action_time for wallet in db.all(
                            Wallet, Wallet.initial_completed.is_(False)
                        )))
                        logger.info(f'The next closest action will be performed at {unix_to_strtime(next_action_time)}.')
                    except:
                        pass

                db.commit()

            else:
                if next_message_time <= now:
                    next_message_time = now + 30 * 60
                    logger.success('Wallets are over!')

        except BaseException as e:
            logger.exception('initial')
            logger.error(f'Something went wrong: {e}')

        finally:
            await asyncio.sleep(delay)
