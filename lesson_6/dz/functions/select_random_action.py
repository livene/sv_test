from loguru import logger
import random

from py_eth_async.client import Client
from py_eth_async.data.models import Networks

from tasks.controller import Controller
from db_api.models import Wallet
from data.models import Contracts, Settings


async def select_random_action(controller: Controller, wallet: Wallet, initial: bool = False):
    settings = Settings()
    possible_actions = []
    weights = []

    stargate_swaps = 0
    coredao_swaps = 0
    testnetbridge_swaps = 0
    if initial:
        stargate_swaps = await controller.count_stargate_swaps()
        coredao_swaps = await controller.count_coredao_swaps()
        testnetbridge_swaps = await controller.count_testnetbridge_swaps()
        logger.debug(f'{controller.client.account.address}: '
                     f'stargate_swaps: {stargate_swaps}/{wallet.stargate_swaps}; '
                     f'coredao_swaps: {coredao_swaps}/{wallet.coredao_swaps} '
                     f'testnetbridge_swaps: {testnetbridge_swaps}/{wallet.testnetbridge_swaps}')

        if stargate_swaps >= wallet.stargate_swaps and \
                coredao_swaps >= wallet.coredao_swaps and \
                testnetbridge_swaps >= wallet.testnetbridge_swaps:
            return 'Processed'

    if stargate_swaps < wallet.stargate_swaps:
        network_with_usdc = await controller.stargate.get_network_with_usdc(address=controller.client.account.address)
        if network_with_usdc:
            possible_actions.append(controller.stargate.action)
            weights.append(0.2)
        else:
            logger.debug(f'{controller.client.account.address} | no usdc balance')

    if coredao_swaps < wallet.coredao_swaps:
        bsc_client = Client(
            private_key=controller.client.account.key, network=Networks.BSC, proxy=controller.client.proxy)
        usdt_balance = await bsc_client.wallet.balance(token=Contracts.BSC_USDT)
        if usdt_balance.Ether >= settings.coredao_swaps_amount.to_:
            possible_actions.append(controller.coredao.action)
            weights.append(0.2)
        else:
            logger.debug(f'{controller.client.account.address} | not enough usdt balance ({usdt_balance.Ether})')

    if testnetbridge_swaps < wallet.testnetbridge_swaps:
        arbitrum_client = Client(
            private_key=controller.client.account.key, network=Networks.Arbitrum, proxy=controller.client.proxy)
        geth_balance = await arbitrum_client.wallet.balance(token=Contracts.ARBITRUM_GETH)
        if geth_balance.Ether < settings.testnetbridge_swaps_amount.to_:
            possible_actions.append(controller.uniswap.action)
            weights.append(0.5)
        else:
            possible_actions.append(controller.testnetbridge.action)
            weights.append(0.2)

    if possible_actions:
        action = None
        while not action:
            action = random.choices(possible_actions, weights=weights)[0]
        else:
            return action

    logger.info(f'{controller.client.account.address} | select_random_action | can not choose the action')
    return None
