import os
from pathlib import Path

from ib_insync import IB


def load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        os.environ.setdefault(key.strip(), value.strip())


load_env_file(Path(__file__).with_name('.env'))
ib_account_id = os.getenv('IB_ACCOUNT_ID', '').strip()

ib = IB()
ib.connect('127.0.0.1', 4001, clientId=4)

positions = ib.positions()
if not positions:
    print('No positions found.')
else:
    print('Current positions:')
    for pos in positions:
        if ib_account_id and pos.account != ib_account_id:
            continue
        print(f"{pos.account} {pos.contract.symbol} {pos.position} @ {pos.avgCost}")

ib.disconnect()
