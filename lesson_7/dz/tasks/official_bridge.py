import random
from loguru import logger
from tasks.base import Base
from py_eth_async.data.models import TxArgs, TokenAmount
from data.models import Contracts, Networks
from py_eth_async.data.models import Wei, GWei
from data.models import zkSync
from web3.types import TxParams


class OfficialBridge(Base):
    async def deposit(self, amount: TokenAmount) -> str:
        failed_text = f'Failed bridge ETH to ZkSync via Official Bridge'

        if self.client.network.name != Networks.Ethereum.name:
            return f'{failed_text} | wrong network ({self.client.network.name})'

        balance = await self.client.wallet.balance()
        gas_price = await self.client.transactions.gas_price(w3=self.client.w3)
        gas_limit = 149_210
        transaction_fee = gas_price * gas_limit

        if amount >= balance:
            amount = balance - transaction_fee * 2
            if amount.Wei <= 0:
                return f'{failed_text}: to low balance ({balance.Ether})'

        contract = await self.client.contracts.get(contract_address=Contracts.OFFICIAL_BRIDGE_ETH)

        l2_gas_limit = random.randint(763252, 793252)
        # https://era.zksync.io/docs/dev/how-to/send-transaction-l1-l2.html#step-by-step
        max_fee = Wei(await contract.functions.l2TransactionBaseCost(gas_price.Wei, l2_gas_limit, 800).call())

        logger.info(
            f'{self.client.account.address} | OfficialBridge | to_zksync | amount: {amount.Ether}, transaction_fee: {transaction_fee.Ether} | bridge_fee: {max_fee.Ether}'
        )
        if balance < amount + transaction_fee + max_fee:
            return f'{failed_text}: insufficient balance.'

        args = TxArgs(
            _contractL2=self.client.account.address,
            _l2Value=amount.Wei,
            _calldata=self.client.w3.to_bytes(text=''),
            _l2GasLimit=l2_gas_limit,
            _l2GasPerPubdataByteLimit=800,
            _factoryDeps=[],
            _refundRecipient=self.client.account.address
        )

        max_priority_fee_per_gas = GWei(1.5)
        tx_params = {
            'maxPriorityFeePerGas': max_priority_fee_per_gas.Wei,
            'maxFeePerGas': (await self.get_max_fee_per_gas(max_priority_fee_per_gas=max_priority_fee_per_gas)).Wei,
            'to': contract.address,
            'data': contract.encodeABI('requestL2Transaction', args=args.tuple()),
            'value': amount.Wei + max_fee.Wei
        }

        tx = await self.client.transactions.sign_and_send(tx_params=tx_params)
        receipt = await tx.wait_for_receipt(client=self.client, timeout=300)
        if receipt:
            return f'{amount.Ether} ETH was bridged to ZkSynk via Official Bridge: {tx.hash.hex()}'
        return f'{failed_text}!'

    async def withdraw(self, amount: TokenAmount) -> str:
        failed_text = 'Failed to bridge to Ethereum'

        if self.client.network.name != zkSync:
            return f'{failed_text} | wrong network ({self.client.network.name})'

        logger.info(
            f'{self.client.account.address} | OfficialBridge | withdraw | amount: {amount.Ether}'
        )

        contract = await self.client.contracts.get(contract_address=Contracts.OFFICIAL_BRIDGE_ZKSYNC)

        args = TxArgs(
            _l1Receiver=self.client.account.address
        )
        tx_params = TxParams(
            to=contract.address,
            data=args.tuple(),
            value=amount.Wei
        )

        tx = await self.client.transactions.sign_and_send(tx_params=tx_params)
        receipt = await tx.wait_for_receipt(client=self.client, timeout=300)
        if receipt:
            return f'ETH was withdraw to Ethereum via the official bridge: {tx.hash.hex()}'
        return f'{failed_text}!'
