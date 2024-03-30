from web3 import Web3
from loguru import logger
from db_api.models import Wallet
from withdrawal.okx_actions import OKXActions
from py_okx_async.models import Chains

from client import StarknetClient, EthClient
from utils.utils import randfloat, sleep_delay
from data.models import Settings, TokenAmount
from data.config import ETH_RPC


def get_evm_balance(address: str):
    address = Web3.to_checksum_address(address)
    web3 = Web3(Web3.HTTPProvider(endpoint_uri=ETH_RPC))
    return TokenAmount(amount=web3.eth.get_balance(address), wei=True)


async def okx_withdraw(wallets: list[Wallet]):
    settings = Settings()
    okx = OKXActions(credentials=settings.okx.credentials)

    for num, wallet in enumerate(wallets, start=1):
        logger.info(f'{num}/{len(wallets)} wallets')
        if settings.use_official_bridge:
            address = wallet.evm_wallet_address
            balance = get_evm_balance(address=address)
        else:
            private_key = int(wallet.private_key, 16)
            address = int(wallet.address, 16)
            eth_client = EthClient(private_key=wallet.evm_wallet_private_key)
            async with StarknetClient(
                    private_key=private_key,
                    account_address=int(wallet.address, 16),
                    proxy=wallet.proxy
            ) as starknet_client:
                balance = await starknet_client.get_balance()

        if not address or float(balance.Ether) >= settings.minimal_balance:
            continue

        amount_to_withdraw = randfloat(
            from_=settings.okx.withdraw_amount.from_,
            to_=settings.okx.withdraw_amount.to_,
            step=0.0000001
        )
        amount_to_withdraw = amount_to_withdraw - float(balance.Ether)

        res = await okx.withdraw(
            to_address=eth_client.account.address if settings.use_official_bridge else wallet.address,
            amount=amount_to_withdraw,
            token_symbol='ETH',
            chain=Chains.ERC20 if settings.use_official_bridge else 'StarkNet'
        )
        if 'Failed' not in res:
            logger.success(f'{wallet.name}: {res}')
            if num == len(wallets):
                logger.success(f'OKX withdraw successfully completed with {len(wallets)} wallets')
                continue
            await sleep_delay(okx=True)
        else:
            logger.error(f'{wallet.name}: {res}')
