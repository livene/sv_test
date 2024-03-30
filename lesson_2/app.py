import asyncio
from eth_account import Account
import secrets
from lesson_2.sdk.data.models import Networks
from lesson_2.sdk.client import Client
from private_data import proxy
from loguru import logger


async def generate_private(max_keys=10):
    private_keys = []
    for _ in range(max_keys):
        private_key = Account.create(secrets.token_bytes(32))._private_key
        logger.info(private_keys.append(private_key.hex()))
        await asyncio.sleep(0.05)
    return private_keys


async def check_balance(private_keys):
    for key in private_keys:
        client = Client(private_key=key, network=Networks.Ethereum, proxy=proxy)
        balance = await client.wallet.balance()
        logger.info(f'balance: {balance} | private_key: {key} | address: {client.account.address}')


async def main():
    private_keys = await generate_private()
    await check_balance(private_keys)


if __name__ == '__main__':
    asyncio.run(main())
