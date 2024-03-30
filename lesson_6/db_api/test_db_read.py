from db_api.database import session
from db_api.models import Wallet


# обращения к базе не происходит (ленивая сессия)
q = session.query(Wallet).filter(Wallet.coredao_swaps >= 5).filter_by(completed=False).filter_by()
# print(q)

# обращение к базе только во время считывания
print(q.count())


# посметреть все объекты по-очереди
# for wallet in q:
#     print(wallet.address)

# получить первый объект
wallet = q.first()
print(wallet.address)

print(session.dirty)

wallet.coredao_swaps = 100
print(session.dirty)

# если хотим, чтобы изменения сохранились, не забываем коммитить сессию
session.commit()
