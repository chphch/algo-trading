import asyncio
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
ib.connect('127.0.0.1', 4001, clientId=3)

print("기존 BTC 포지션을 정리합니다...")

# 포지션 확인
positions = ib.positions()
btc_qty = 0
for pos in positions:
    if pos.contract.symbol == 'BTC' and pos.account == IB_ACCOUNT_ID:
        btc_qty = pos.position
        print(f"현재 BTC 보유량: {btc_qty:.8f}")
        break

if btc_qty > 0:
    # BTC 계약
    contract = Crypto('BTC', 'PAXOS', 'USD')
    ib.qualifyContracts(contract)
    
    # 전량 매도 (수량 기반)
    sell_order = MarketOrder('SELL', btc_qty)
    sell_order.tif = 'IOC'
    if IB_ACCOUNT_ID:
        sell_order.account = IB_ACCOUNT_ID
    
    trade = ib.placeOrder(contract, sell_order)
    print(f"매도 주문 전송... (수량: {btc_qty:.8f} BTC)")
    
    # 체결 대기
    ib.sleep(5)
    
    if trade.isDone():
        print(f"✓ 매도 완료: {trade.orderStatus.filled} BTC @ ${trade.orderStatus.avgFillPrice}")
    else:
        print(f"주문 상태: {trade.orderStatus.status}")
else:
    print("BTC 포지션이 없습니다.")

ib.disconnect()
