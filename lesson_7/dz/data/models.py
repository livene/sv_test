from typing import Optional, Union
from dataclasses import dataclass
import json

from pretty_utils.type_functions.classes import Singleton, AutoRepr
from py_eth_async.data.models import Network, Networks, GWei, RawContract, DefaultABIs
from pretty_utils.miscellaneous.files import read_json

from data.config import ABIS_DIR, SETTINGS_PATH


zkSync = Network(
    name='zksync',
    rpc='https://mainnet.era.zksync.io',
    chain_id=324,
    tx_type=0,
    coin_symbol='ETH',
    explorer='https://explorer.zksync.io/',
)

OfficialBridgeZkSyncABI = [
    {
        'constant': False,
        'inputs': [
            {'name': '_l1Receiver', 'type': 'address'},
        ],
        'name': 'withdraw',
        'outputs': [],
        'payable': True,
        'stateMutability': 'payable',
        'type': 'function'
    }
]


class Contracts(Singleton):
    # zkSync
    MUTE = RawContract(
        address='0x8b791913eb07c32779a16750e3868aa8495f5964', abi=read_json(path=(ABIS_DIR, 'mute.json'))
    )

    WETH = RawContract(
        address='0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91', abi=read_json(path=(ABIS_DIR, 'WETH.json'))
    )

    USDC = RawContract(
        address='0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4', abi=DefaultABIs.Token
    )

    SYNCSWAP = RawContract(
        address='0x2da10A1e27bF85cEdD8FFb1AbBe97e53391C0295', abi=read_json(path=(ABIS_DIR, 'syncswap.json'))
    )

    SPACEFI = RawContract(
        address='0xbe7d1fd1f6748bbdefc4fbacafbb11c6fc506d1d', abi=read_json(path=(ABIS_DIR, 'space_fi.json'))
    )

    USDC_WETH_cSLP = RawContract(
        address='0x80115c708E12eDd42E504c1cD52Aea96C547c05c', abi=DefaultABIs.Token
    )

    OFFICIAL_BRIDGE_ZKSYNC = RawContract(
        address='0x000000000000000000000000000000000000800A', abi=json.dumps(OfficialBridgeZkSyncABI)
    )

    # Ethereum
    OFFICIAL_BRIDGE_ETH = RawContract(
        address='0x32400084c286cf3e17e7b677ea9583e60a000324', abi=read_json(path=(ABIS_DIR, 'official_bridge.json'))
    )


class InitialCsvData:
    HEADER = ['private_key', 'name', 'proxy']

    def __init__(self, private_key: str, name: str = '', proxy: str = ''):
        self.private_key = private_key
        self.name = name
        self.proxy = proxy


@dataclass
class FromTo:
    from_: Union[int, float]
    to_: Union[int, float]


class Settings(Singleton, AutoRepr):
    def __init__(self):
        json = read_json(path=SETTINGS_PATH)

        self.oklink_api_key = json['oklink_api_key']

        self.maximum_gas_price: GWei = GWei(json['maximum_gas_price'])
        self.minimal_balance: float = json['minimal_balance']
        self.initial_actions_delay: FromTo = FromTo(
            from_=json['initial_actions_delay']['from'], to_=json['initial_actions_delay']['to']
        )
        self.swaps: FromTo = FromTo(from_=json['swaps']['from'], to_=json['swaps']['to'])
        self.activity_actions_delay: FromTo = FromTo(
            from_=json['activity_actions_delay']['from'], to_=json['activity_actions_delay']['to']
        )
        self.eth_amount_for_swap: FromTo = FromTo(
            from_=json['eth_amount_for_swap']['from'], to_=json['eth_amount_for_swap']['to']
        )
