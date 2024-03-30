from db_api.models import Wallet
from db_api.database import db


wallets = db.all(Wallet, Wallet.id.is_(1), Wallet.address.startswith('0x'))
for wallet in wallets:
    print(wallet)
