from typing import Optional

from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import create_engine

from db_api.models import Base, Wallet
from db_api.db import DB


def get_wallets(sqlite_query: bool = False) -> list[Wallet]:
    if sqlite_query:
        return db.execute('SELECT * FROM wallets')

    return db.all(Wallet)


def get_wallet(private_key: str, sqlite_query: bool = False) -> Optional[Wallet]:
    if sqlite_query:
        return db.execute('SELECT * FROM wallets WHERE private_key = ?', (private_key,), True)

    return db.one(Wallet, Wallet.private_key == private_key)


# engine = create_engine('sqlite:///wallets.db', echo=False)
# Base.metadata.create_all(engine)
# session = sessionmaker(bind=engine)()

# pool_recycle=3600 - это параметр, определяющий,
#   как долго должны оставаться активные подключения в пуле перед их пересозданием.
# check_same_thread устанавливается в False, что позволяет использовать подключение в разных потоках.
db = DB('sqlite:///files/wallets.db', echo=False, pool_recycle=3600, connect_args={'check_same_thread': False})
db.create_tables(Base)
