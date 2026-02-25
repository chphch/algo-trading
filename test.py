import asyncio
import os
from pathlib import Path

import pandas_ta as ta
from ib_insync import *
from decimal import Decimal


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
if not IB_ACCOUNT_ID:
    print("Warning: IB_ACCOUNT_ID is not set. Orders may fail without an account.")

# 1. 연결 설정
ib = IB()
# 포트번호 확인: 실전 4001, 모의 4002
ib.connect('127.0.0.1', 4001, clientId=1)

# 2. 비트코인 컨트랙트 설정 (PAXOS 거래소 경유)
contract = Crypto('BTC', 'PAXOS', 'USD')
ib.qualifyContracts(contract)

async def trade_logic():
    count = 0
    limit = 5  # 총 5번 실행

    print(f"알고리즘 시작: {limit}회 반복 예정")

    while count < limit:
        # 실시간 데이터 가져오기 (RSI 계산을 위해 1시간 분량의 1분봉 요청)
        bars = await ib.reqHistoricalDataAsync(
            contract, endDateTime='', durationStr='3600 S',
            barSizeSetting='1 min', whatToShow='AGGTRADES', useRTH=True
        )
        
        if not bars:
            print("데이터를 가져올 수 없습니다. 재시도 중...")
            await asyncio.sleep(1)
            continue

        df = util.df(bars)
        
        # RSI 계산 (RSI 1 이상은 사실상 모든 시점에서 참입니다)
        df['RSI'] = ta.rsi(df['close'], length=14)
        current_rsi = df['RSI'].iloc[-1]
        current_price = df['close'].iloc[-1]

        print(f"[{count+1}/{limit}] 현재가: {current_price}, RSI: {current_rsi:.2f}")

        # 조건 체크: RSI가 1 이상이면 실행
        if current_rsi >= 1:
            # 매수 주문 (cashQty 사용 - IB의 crypto 요구사항)
            buy_order = MarketOrder('BUY', 0)
            buy_order.cashQty = 6  # 6달러만큼 매수
            buy_order.tif = 'GTC'  # Good Till Cancel
            if IB_ACCOUNT_ID:
                buy_order.account = IB_ACCOUNT_ID
            buy_trade = ib.placeOrder(contract, buy_order)
            print(f"매수 주문 전송... (금액: $6)")
            
            # 매수 주문이 체결될 때까지 대기
            await asyncio.sleep(2)
            
            # 포지션 확인하여 보유 수량 조회
            positions = ib.positions()
            btc_qty = 0
            for pos in positions:
                if pos.contract.symbol == 'BTC':
                    btc_qty = pos.position
                    break
            
            if btc_qty > 0:
                # 매도 주문 (보유한 BTC 전체 매도)
                sell_order = MarketOrder('SELL', btc_qty)
                sell_order.tif = 'GTC'
                if IB_ACCOUNT_ID:
                    sell_order.account = IB_ACCOUNT_ID
                sell_trade = ib.placeOrder(contract, sell_order)
                print(f"매도 주문 전송... (수량: {btc_qty})")
            else:
                print("매수 체결 대기 중... BTC 포지션 없음")
            
            count += 1
        else:
            print("RSI 조건 미달")

        # 1초 대기
        await asyncio.sleep(1)

    print("5회 반복 완료. 프로그램을 종료합니다.")
    ib.disconnect()

# 비동기 루프 실행
ib.run(trade_logic())