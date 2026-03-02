# Crypto Auto Trading BOT

## 📁 프로젝트 아키텍처 (Project Architecture)

```text
Crypto_Auto_Trading-BOT/
├── src/
│   ├── indicators.py      # Custom Indicators (AWMA, KAMA, MFI 계산 - Snippet 1)
│   ├── strategy.py        # Dynamic Scaling & Early Exit 로직 (Snippet 2, 3)
│   ├── execution.py       # CCXT Order Wrapper, Hard SL 방어망, Paper Trading (Snippet 4, 7)
│   └── data_loader.py     # History + Live Data Sync 파이프라인 (Snippet 5)
│
├── research/
│   ├── optimizer.py       # Grid Search Parameter Optimizer (Snippet 6)
│   └── backtester.py      # 과거 데이터 전진 분석(Walk-forward) 엔진
│
├── config/                # 프로덕션 환경 분리
│   ├── settings.yaml      # 트레이딩 파라미터 (레버리지, 타겟 기댓값 등)
│   └── .env.example       # API Key 및 텔레그램 토큰 관리
│
├── utils/                 # 모니터링 및 로깅
│   └── logger.py          # 텔레그램 알림 및 시스템 에러 로깅
│
├── main.py                # 24/365 봇 실행 메인 비동기 루프
└── requirements.txt       # 의존성 패키지 명세
```

---

## 1. 적응형 가중 이동평균(AWMA/KAMA) 자체 구현 로직 (`src/indicators.py`)
**[문제 상황 및 개선 방식]**
기존 단순 이동평균선(SMA)은 횡보장에서 발생하는 가격 교차에 취약하여 잦은 휩쏘(Whipsaw)와 불필요한 손절을 유발하는 문제점이 있었습니다. 이를 개선하기 위해 외부 패키지(TA-Lib 등)에 의존하지 않고, 변동성(추세 강도)에 따라 반응 계수가 기민하게 조절되는 적응형 이동평균선(KAMA)을 First Principles 기반의 순수 Python/Numpy 연산으로 구현하여 시계열 데이터의 노이즈 필터링 성능을 확보했습니다.

## 2. 3-Stage 동적 피라미딩(Scaling in) 주문 실행 로직 (`src/strategy.py`)
**[문제 상황 및 개선 방식]**
단일 시점 일괄(All-in/All-out) 진입 방식은 추세 분출 시 손익비(Risk/Reward) 극대화에 구조적 한계가 있었습니다. 이를 해결하기 위해 시장 방향성이 검증된 시점(포지션이 일정 수준의 수익권에 안착 시)에만 잔여 물량을 단계별로 투입하는 조건부 피라미딩(Conditional Scaling-in) 로직을 설계하여 무의미한 초기 진입 손실 위험을 회피하고 자본 효율을 큰 폭으로 개선했습니다.

## 3. 마켓 레짐 진단 및 변곡점 조기 청산 (`src/strategy.py`)
**[문제 상황 및 개선 방식]**
단일 목표가 기반의 분할 청산 로직만으로는 과매수/과매도 구간의 급박한 추세 반전에 선제적으로 대응하기 어려웠습니다. 상승 모멘텀의 고갈을 파악하기 위해 파생 지표(Money Flow Index)의 극단값과 가격 추세의 이탈(Divergence)이 겹치는 시그널을 구조화하였고, 시그널 관측 시 즉각적으로 전량 탈출하는 동적 리스크 관리 기능을 추가하여 변동성 위험을 해소했습니다.

## 4. 하드 스탑 방어(Flash Crash Protection) 아키텍처 (`src/execution.py`)
**[문제 상황 및 개선 방식]**
소프트 스탑로스(Soft Stop-loss)는 로컬 클라우드 봇 프로세스 지연이나 급등락장(Flash Crash)에서의 API 병목 현상 발생 시 주문이 누락되어 계좌의 치명적 손실을 초래할 리스크가 컸습니다. 이를 방지하기 위해 포지션 진입과 동시에 거래소 매칭 서버에 종속되는 하드 스탑로스(Hard Stop-Loss) 주문을 직접 발주시키는 이중 안전 체계를 구축함으로써 로컬 시스템 장애에 대비한 자본 보존력을 보장했습니다.

## 5. Live-Simulation 및 Deep Warm-up 아키텍처 (`src/data_loader.py`)
**[문제 상황 및 개선 방식]**
알고리즘 배포 직후 실시간 API 데이터 통신에만 의존할 경우, 장기 지표 계산에 필요한 초기 캔들 누락으로 결측값(Cold Start) 지연이 발생하는 한계가 존재했습니다. 이를 해결하고자 과거 수년 치의 캐시 데이터(Pickle Base)와 최신화된 실시간 호가 API 사이의 연속성을 연결 후 중복 없이 병합(Merge & Deduplicate)하는 파이프라인 구조를 개발해 봇 가동 즉시 딜레이 없는 지표 산출과 거래 개시를 달성했습니다.

## 6. 그리드 서치(Grid Search) 최적화 도구 및 시스템 견고성 검증 (`research/optimizer.py`)
**[문제 상황 및 개선 방식]**
단일 모델의 최고 PnL 최적화 수치에만 매몰될 시, 강한 과최적화(Curve-fitting)로 인해 새로운 시장 환경에서 전략이 붕괴하는 한계점이 있었습니다. 모델의 통계적 견고함(Robustness) 검증을 위해 `joblib` 연산 코어 베이스의 **Grid Search 툴**을 개발하여 공간 내 파라미터 유니버스를 전수 검증했습니다. 단순히 이익 편향 지점이 아닌, MDD가 억제되며 Sharpe Ratio의 일관성이 방어되는 '안정 구역(Robust Plateau)' 모델링을 특정하여 실매매 투입 기준을 확립했습니다.

## 7. 가상 모의투자(Paper Trading) 원장 관리 시스템 (`src/execution.py`)
**[문제 상황 및 개선 방식]**
신규 알고리즘을 즉시 API 체결 루프에 올릴 시 논리적 버그(Logical Bug)로 인한 영구적 자본 손실(Execution Risk) 리스크가 있었습니다. 이를 제한하기 위해, 거래소 호가 데이터는 실시간으로 수신하되 실제 주문 전송은 차단(Circuit Breaker)하고 그 내역을 로컬 메모리 가상 원장상(In-Memory DB) 업데이트로 시뮬레이션하는 Paper Trading 전진 분석 엔진 아키텍처를 도입했습니다. 환경 변수 스위치만으로 가상거래와 실매매를 즉각 전환(Hot-swap) 가능하도록 추상화하여, 시장 충격(Slippage)과 거래 수수료(Fee)가 반영된 실환경 동일 테스트를 자본 리스크 없이 수행하도록 개선했습니다.
