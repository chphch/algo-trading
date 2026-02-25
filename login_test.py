from ib_insync import *

# 1. 객체 생성
ib = IB()

# 2. 연결 (IP, 포트, 클라이언트ID)
# 포트: Gateway 모의투자는 보통 4002, 실전은 4001
try:
    ib.connect('127.0.0.1', 4001, clientId=1)
    print("연결 성공!")
    
    # 3. 계좌 잔고 및 포지션 확인
    print(f"계좌 리스트: {ib.managedAccounts()}")
    print(f"현재 포지션: {ib.positions()}")

except Exception as e:
    print(f"연결 실패: {e}")

# 4. 종료 시 연결 해제
ib.disconnect()
