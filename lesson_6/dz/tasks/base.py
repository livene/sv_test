import asyncio
from typing import Union, Optional

import aiohttp
from py_eth_async.client import Client
from py_eth_async.data.models import TokenAmount, CoinTx, Network
from py_eth_async.data import types
from py_eth_async.utils import api_key_required

from data.config import logger


class Base:
    def __init__(self, client: Client):
        self.client = client

    async def get_decimals(self, contract_address: str) -> int:
        contract = await self.client.contracts.default_token(contract_address=contract_address)
        return await contract.functions.decimals().call()

    async def approve_interface(self, token_address: str, spender: str, amount: Optional[TokenAmount] = None) -> bool:
        logger.info(
            f'{self.client.account.address} | start approve token_address: {token_address} for spender: {spender}'
        )
        balance = await self.client.wallet.balance(token=token_address)
        if balance.Wei <= 0:
            logger.error(f'{self.client.account.address} | approve | zero balance')
            return False

        if not amount or amount.Wei > balance.Wei:
            amount = balance

        approved_amount = await self.client.transactions.approved_amount(
            token=token_address,
            spender=spender
        )
        if amount.Wei <= approved_amount.Wei:
            return True
        tx = await self.client.transactions.approve(
            token=token_address,
            spender=spender,
            amount=amount
        )
        receipt = await tx.wait_for_receipt(client=self.client, timeout=200)
        if receipt:
            return True
        return False

    async def get_token_price(self, token='ETH', retries: int = 5):
        token = token.upper()
        for _ in range(retries):
            try:
                async with aiohttp.ClientSession() as session:
                    logger.info(
                        f'{self.client.account.address} | getting {token} price')
                    async with session.get(f'https://api.binance.com/api/v3/depth?limit=1&symbol={token}USDT') as r:
                        if r.status != 200:
                            logger.error(f'code: {r.status} | json: {r.json()}')
                            exit()
                        result_dict = await r.json()
                        if 'asks' not in result_dict:
                            logger.error(
                                f'code: {r.status} | json: {r.json()}')
                            exit()
                        return float(result_dict['asks'][0][0])
            except Exception as e:
                logger.error(
                    f'{self.client.account.address} | getting {token} price: {e}')
                await asyncio.sleep(5)
        exit()

    @api_key_required
    async def find_txs_by_method_id(
            self,
            contract: Union[types.Contract, list[types.Contract]],
            method_id: Optional[str] = '',
            network: Optional[Network] = None,
            address: Optional[types.Address] = None,
            after_timestamp: int = 0,
            before_timestamp: int = 999_999_999_999
    ) -> dict[str, CoinTx]:

        private_key = self.client.account.key if self.client.account.key else ''
        used_network = network if network else self.client.network

        client = Client(private_key=private_key, network=used_network, proxy=self.client.proxy)

        contract_addresses = []
        if isinstance(contract, list):
            for contract_ in contract:
                contract_address, abi = await client.contracts.get_contract_attributes(contract_)
                contract_addresses.append(contract_address.lower())

        else:
            contract_address, abi = await self.client.contracts.get_contract_attributes(contract)
            contract_addresses.append(contract_address.lower())

        if not address:
            address = self.client.account.address

        txs = {}
        coin_txs = (await client.network.api.functions.account.txlist(address))['result']

        for tx in coin_txs:
            if (
                    after_timestamp < int(tx.get('timeStamp')) < before_timestamp and
                    tx.get('isError') == '0' and
                    tx.get('to') in contract_addresses and
                    method_id in tx.get('methodId')
            ):
                txs[tx.get('hash')] = CoinTx(data=tx)

        return txs
