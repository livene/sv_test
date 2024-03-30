from db_api.database import session
from db_api.models import Wallet


# 1 способ удаления
# удалит объект сразу (мы его даже посмотреть не сможем)
# q = session.query(Wallet).filter_by(address='11111').delete()
# session.commit()


# 2 способ удаления
# получили нужные нам объекты
q = session.query(Wallet).filter_by(address='22222')
# достали только первый из них
wallet = q.first()
print(wallet.address)
# удаляем этот объект
session.delete(wallet)
session.commit()
