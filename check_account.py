import os
from pathlib import Path
from ib_insync import *

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
IB_ACCOUNT_ID = os.getenv('IB_ACCOUNT_ID', '').strip()

# 연결
ib = IB()
ib.connect('127.0.0.1', 4001, clientId=2)

print("=" * 60)
print("계정 정보 확인")
print("=" * 60)

# 계좌 정보
account_values = ib.accountValues()
print("\n[계좌 잔액 정보]")
for av in account_values:
    if av.account == IB_ACCOUNT_ID:
        if av.tag in ['NetLiquidation', 'TotalCashValue', 'BuyingPower', 'AvailableFunds']:
            print(f"{av.tag}: {av.value} {av.currency}")

# 포지션
print("\n[현재 포지션]")
positions = ib.positions()
if positions:
    for pos in positions:
        if pos.account == IB_ACCOUNT_ID:
            print(f"{pos.contract.symbol}: {pos.position} @ {pos.avgCost}")
else:
    print("포지션 없음")

# 암호화폐 계약 테스트
print("\n[암호화폐 계약 테스트]")
try:
    contract = Crypto('BTC', 'PAXOS', 'USD')
    details = ib.qualifyContracts(contract)
    if details:
        print(f"✓ BTC 계약 확인 완료: {details[0]}")
    else:
        print("✗ BTC 계약을 찾을 수 없습니다")
except Exception as e:
    print(f"✗ 에러: {e}")

print("\n" + "=" * 60)
print("암호화폐 거래 권한 확인:")
print("- Error 10275가 보이면: 암호화폐 계정 승인 대기 중")
print("- 에러가 없으면: 암호화폐 거래 가능")
print("=" * 60)

ib.disconnect()
