import aiohttp
import asyncio
from typing import Union, Optional
from fake_useragent import UserAgent

from data.config import logger
from proxy_client import StarknetClient
from data.models import TokenAmount


class Base:
    def __init__(self, starknet_client: StarknetClient):
        self.starknet_client = starknet_client

    @staticmethod
    async def get_token_price(token_symbol='ETH', default_value=-1) -> Union[int, float]:
        token_symbol = token_symbol.upper()
        params = {
            'fsym': token_symbol,
            'tsyms': 'USD'
        }
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    logger.info(
                        f'getting {token_symbol} price')
                    async with session.get(
                            f'https://min-api.cryptocompare.com/data/price', params=params
                    ) as r:
                        result_dict = await r.json()
                        if 'HasWarning' in result_dict and not result_dict['HasWarning']:
                            logger.error(
                                f'getting {token_symbol} price | {result_dict["Message"]}'
                            )
                            return default_value

                        return result_dict['USD']

            except Exception as e:
                logger.error(f'getting {token_symbol} price: {e}')
                await asyncio.sleep(5)

    @staticmethod
    async def get_amount_out(
            amount_in: TokenAmount,
            slippage: float = 1.,
            token_in_name: str = 'ETH',
            token_out_name: str = 'STABLE',
            amount_out_dicimals: int = 18
    ) -> TokenAmount:
        token_in_name, token_out_name = token_in_name.upper(), token_out_name.upper()

        token_in_usd = await Base.get_token_price(token_symbol=token_in_name)
        token_out_usd = 1 if token_out_name == 'STABLE' else await Base.get_token_price(token_symbol=token_out_name)

        return TokenAmount(
            amount=token_in_usd / token_out_usd * float(amount_in.Ether) * (100 - slippage) / 100,
            decimals=amount_out_dicimals
        )

    async def _get_txs(self, account_address: Optional[str] = None, page: int = 1):
        if not account_address:
            account_address = self.starknet_client.hex_address
        headers = {
            'authority': 'api.viewblock.io',
            'accept': '*/*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'origin': 'https://viewblock.io',
            'referer': 'https://viewblock.io/',
            'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': UserAgent().chrome,
        }

        params = {
            'page': page,
            'network': 'mainnet',
        }

        url = f'https://api.viewblock.io/starknet/contracts/{account_address}/txs'

        async with aiohttp.ClientSession(connector=self.starknet_client.connector) as session:
            async with await session.get(
                    url,
                    params=params,
                    headers=headers
            ) as r:
                result = (await r.json())
                return result['pages'], result['docs']

    async def get_txs(self, account_address: Optional[str] = None) -> list:
        if not account_address:
            account_address = self.starknet_client.hex_address
        page = 1
        txs_lst = []
        pages, txs = await self._get_txs(account_address=account_address, page=page)
        txs_lst += txs
        if pages == 0:
            return []
        while page < pages:
            page += 1
            pages, txs = await self._get_txs(account_address=account_address, page=page)
            txs_lst += txs
        return txs_lst

    async def find_txs(
            self,
            to: str,
            function_names: list,
            txs: Optional[list[dict]] = None,
            status: str = ('ACCEPTED_ON_L1', 'ACCEPTED_ON_L2')
    ) -> list[dict]:
        if txs is None:
            txs = await self.get_txs(account_address=self.starknet_client.hex_address)

        result_txs = []

        for tx in txs:
            try:
                for call in tx['decoded'].get('calls', []):
                    call_to = call['to'].lower()

                    if call_to == to.lower() and call['name'] in function_names and tx['status'] in status:
                        result_txs.append(tx)
                        break
            except KeyError:
                continue

        return result_txs
