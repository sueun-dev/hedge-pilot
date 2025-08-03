# Bithumb 거래소 테스트 가이드

## 테스트 구성

### 1. 단위 테스트 (`test_bithumb.py`)
실제 API를 사용하는 종합 테스트 파일입니다.

**테스트 카테고리:**
- 연결 및 인증 테스트
- 마켓 데이터 테스트
- 계정 정보 테스트
- 주문 테스트
- GNO 코인 매매 시나리오
- 에러 처리 및 엣지 케이스
- 통합 테스트

### 2. 실제 거래 테스트 (`test_live_bithumb.py`)
실제 API를 사용하여 거래를 실행하는 독립 실행 스크립트입니다.

## 환경 설정

### 1. API 키 설정
`.env` 파일에 Bithumb API 키를 설정하세요:

```bash
BITHUMB_API_KEY=your_actual_api_key
BITHUMB_API_SECRET=your_actual_api_secret
```

### 2. 필요 패키지 설치
```bash
pip install python-dotenv ccxt
```

## 테스트 실행 방법

### 방법 1: unittest 직접 실행
```bash
# 모든 테스트 실행
python -m unittest tests.test_bithumb -v

# 특정 클래스 실행
python -m unittest tests.test_bithumb.TestBithumbExchange -v

# 특정 메서드 실행
python -m unittest tests.test_bithumb.TestBithumbExchange.test_get_ticker -v
```

### 방법 2: 테스트 러너 사용
```bash
# 기본 실행 (실제 API 사용)
python tests/run_tests.py

# 특정 모듈 실행
python tests/run_tests.py --module test_bithumb

# 특정 클래스 실행
python tests/run_tests.py --module test_bithumb --class TestBithumbExchange

# 특정 메서드 실행
python tests/run_tests.py --module test_bithumb --class TestBithumbExchange --method test_get_ticker
```

### 방법 3: 실제 거래 테스트 (주의!)
```bash
# 대화형 메뉴로 실행
python tests/test_live_bithumb.py

# 옵션:
# 1. 기본 기능 테스트 (읽기 전용) - 안전
# 2. GNO 코인 매매 시나리오 (실제 거래) - 주의 필요!
# 3. 전체 테스트 실행
```

## 주의사항

⚠️ **중요 경고:**
1. `test_live_bithumb.py`의 옵션 2와 3은 **실제 거래**를 실행합니다
2. 테스트에는 최소 **25,000 KRW**의 잔고가 필요합니다
3. GNO 코인을 실제로 매수/매도합니다
4. 거래 수수료가 발생합니다
5. 시장 상황에 따라 손실이 발생할 수 있습니다

## 안전한 테스트 방법

### 읽기 전용 테스트만 실행
```bash
# 기본 기능 테스트만 (거래 없음)
python tests/test_live_bithumb.py
# 옵션 1 선택
```

### 특정 읽기 테스트만 실행
```bash
# 티커 조회 테스트만
python -m unittest tests.test_bithumb.TestBithumbExchange.test_get_ticker -v

# 잔고 조회 테스트만
python -m unittest tests.test_bithumb.TestBithumbExchange.test_get_balance -v

# 심볼 조회 테스트만
python -m unittest tests.test_bithumb.TestBithumbExchange.test_get_available_symbols -v
```

## 테스트 결과 예시

### 성공적인 실행:
```
=================================================================
Bithumb 실제 API 테스트 시작
=================================================================
✅ API 키 로드 완료
✅ 거래소 초기화 성공

1. 시장 정보 로드 중...
   총 238개의 거래쌍 발견

2. BTC/KRW 티커 조회...
   현재가: 95,000,000 KRW
   매도호가: 95,010,000 KRW
   매수호가: 94,990,000 KRW

3. 계정 잔고 조회...
   KRW 잔고: 100,000 KRW
   사용가능: 100,000 KRW

4. USDT/KRW 환율 조회...
   USDT/KRW: 1,350.00 KRW

✅ 기본 기능 테스트 완료
```

## 문제 해결

### API 키 오류
```
❌ BITHUMB_API_KEY와 BITHUMB_API_SECRET이 .env 파일에 설정되어있지 않습니다
```
→ `.env` 파일에 올바른 API 키를 설정하세요

### 잔고 부족 오류
```
❌ 테스트를 위한 충분한 KRW 잔고가 없습니다 (최소 25,000 KRW 필요)
```
→ 계정에 충분한 KRW를 입금하거나 읽기 전용 테스트만 실행하세요

### 심볼 찾기 오류
```
❌ GNO/KRW 거래쌍을 찾을 수 없습니다
```
→ GNO가 현재 거래 가능한지 확인하거나 다른 코인으로 테스트하세요

## 개발자 노트

- 모든 테스트는 실제 Bithumb API를 사용합니다
- Mock 테스트는 제거되었습니다
- API 호출 간 적절한 지연(0.5~2초)이 적용됩니다
- 8자리 소수점 정밀도로 수량을 계산합니다
- 최소 주문 금액은 1,000 KRW입니다