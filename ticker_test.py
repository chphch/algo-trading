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

# IB 연결
ib = IB()
ib.connect('127.0.0.1', 4001, clientId=2)

# 에러 로깅
def on_error(req_id, error_code, error_string, contract):
    contract_text = f" {contract}" if contract else ""
    print(f"IB error reqId={req_id} code={error_code} msg={error_string}{contract_text}")

ib.errorEvent += on_error

# BTC 컨트랙트
contract = Crypto('BTC', 'PAXOS', 'USD')
ib.qualifyContracts(contract)
print(f"Contract qualified: {contract}")

# 실시간 ticker 구독
ticker = ib.reqMktData(contract, '', False, False)
print("Ticker 구독 시작... 10초간 데이터 수신 대기\n")

async def monitor_ticker():
    for i in range(10):
        await asyncio.sleep(1)
        print(f"[{i+1}s] last={ticker.last} bid={ticker.bid} ask={ticker.ask} "
              f"volume={ticker.volume} time={ticker.time}")
    
    print("\n=== 테스트 완료 ===")
    print(f"최종 ticker 상태: {ticker}")
    ib.cancelMktData(contract)
    ib.disconnect()

ib.run(monitor_ticker())
