from db_api.database import session
from db_api.models import Wallet


# Создание объекта класса Wallet
wallet = Wallet(
    private_key='0x8732y87g23b23y322dsfs',
    address='11111',
    stargate_swaps=2,
    coredao_swaps=3,
    testnetbridge_swaps=4,
)

print(wallet.address)

# id недоступен так как объект еще в в БД
print(wallet.id)

# возвращает список объектов, которые уйдут в БД при коммите
print(session.new)

# добавление объекта в сессию
session.add(wallet)
print(session.new)

# отправляем объект в базу
session.commit()

# id теперь появился
print(wallet.id)


# добавление сразу нескольких объектов (списком)
wallet_2 = Wallet(
    private_key='0x8732y87g23b23y322dsfs22222',
    address='22222',
    stargate_swaps=21,
    coredao_swaps=32,
    testnetbridge_swaps=43,
)
wallet_3 = Wallet(
    private_key='0x8732y87g23b23y322dsfs33333',
    address='33333',
    stargate_swaps=24,
    coredao_swaps=36,
    testnetbridge_swaps=47,
)
session.add_all([wallet_2, wallet_3])
session.commit()
