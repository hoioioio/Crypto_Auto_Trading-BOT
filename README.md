# 📈 Crypto_Auto_Trading-BOT (KAMA 기반 추세 추종 시스템)

본 프로젝트는 바이낸스 선물(Binance Futures) 시장을 타겟으로 한 **데이터 기반의 시스템 트레이딩 엔진**입니다. 시장 변동성에 따라 반응 속도를 조절하는 **적응형 이동평균(AWMA/KAMA)**과 **3단계 피라미딩(Scaling-in)** 로직을 통해 안정적인 우상향 수익 곡선을 추구합니다.

---

## 📊 6개년 백테스트 성과 (2020.01 - 2026.02)
2022년 하락장과 FTX 사태 등 암호화폐 시장의 주요 변동성 구간을 포함한 **6년 간의 데이터** 검증 결과입니다.

| 항목 (Metric) | 수치 (Value) | 비고 |
| :--- | :--- | :--- |
| **누적 수익률 (Net Profit)** | **+3,859.9%** | $1,000 → $39,599 |
| **최대 낙폭 (MDD)** | **8.66%** | 자본 보존 최우선 설계 |
| **소티노 지수 (Sortino Ratio)** | **21.013** | 하방 위험 대비 탁월한 수익 효율성 |
| **샤프 지수 (Sharpe Ratio)** | **0.822** | 리스크 대비 안정적인 성과 |
| **프로핏 팩터 (Profit Factor)** | **2.515** | 총 이익이 총 손실의 2.5배 |
| **승률 (Win Rate)** | **26.50%** | '손절은 짧게, 수익은 길게' |

> **[Insight]** 26.5%의 승률임에도 불구하고 **Sortino Ratio 21.01**을 기록한 것은, 추세 발생 시 **피라미딩(Pyramiding)**을 통해 수익을 극대화하고 횡보장에서 **AWMA**로 손실을 최소화했음을 증명합니다.

---

## 🛠️ 기술 스택 (Tech Stack)
* **Language**: Python 3.x
* **Library**: Pandas, NumPy (Vectorized operation), CCXT, Joblib
* **Monitoring**: Telegram API 실시간 관제 시스템

---

## 📁 프로젝트 아키텍처 (Project Architecture)

```text
Crypto_Auto_Trading-BOT/
├── src/
│   ├── indicators.py      # Custom Indicators (AWMA, KAMA 계산)
│   ├── strategy.py        # Dynamic Scaling & Early Exit 로직
│   ├── execution.py       # CCXT Order Wrapper, Hard SL 방어망, Paper Trading
│   └── data_loader.py     # History + Live Data Sync 파이프라인
│
├── research/
│   ├── optimizer.py       # Grid Search Parameter Optimizer
│   └── backtester.py      # 과거 데이터 전진 분석(Walk-forward) 엔진
│
├── config/                # 프로덕션 환경 분리
│   ├── settings.yaml      # 트레이딩 파라미터 (레버리지, 타겟 기댓값 등)
│   └── .env               # API Key 및 텔레그램 토큰 관리 (.gitignore 처리됨)
│
├── utils/                 # 모니터링 및 로깅
│   └── logger.py          # 시스템 알림 로깅
│
├── main.py                # 24/365 봇 실행 메인 루프
└── requirements.txt       # 의존성 패키지 명세
```

---

## 🔩 Core Engineering Highlights (6 Pillars)

본 프로젝트는 실전 매매의 견고성을 위해 아래 6가지 핵심 기술적 기둥(Pillars)을 바탕으로 설계되었습니다.

### 1. 적응형 가중 이동평균 (KAMA/AWMA) 자체 구현 (`src/indicators.py`)
기존의 단순 이동평균선(SMA)이나 지수 이동평균선(EMA)은 근본적으로 **후행성(Lagging) 지표**라는 치명적인 단점이 있어, 횡보장에서는 잦은 휩쏘(Whipsaw)로 인한 불필요한 손절을 유발했습니다. 이를 극복하기 위해 외부 패키지(TA-Lib 등)에 의존하지 않고, 변동성(추세 강도)에 따라 반응 계수가 기민하게 조절되는 적응형 이동평균선(KAMA)을 First Principles 기반의 순수 Python/Numpy 로 구현했습니다. 이로써 추세장에서는 Fast EMA처럼 기민하게, 횡보장에서는 Slow SMA처럼 둔감하게 반응하여 시계열 노이즈를 완벽하게 필터링합니다.

### 2. 3-Stage 동적 피라미딩 (Scaling in) 주문 실행 (`src/strategy.py`)
단순한 All-in/All-out 진입 방식은 추세 분출 시 손익비(Risk/Reward) 극대화에 한계가 뚜렷했습니다. 이를 해결하기 위해 시장 방향성이 검증된 시점(포지션이 수익권에 도달 시)에만 잔여 물량을 3단계로 나누어 투입하는 조건부 피라미딩(Conditional Scaling-in) 로직을 설계했습니다. 무의미한 초기 진입 손실 위험을 제한하고 기관급 자본 효율성을 달성했습니다.

### 3. 변곡점 조기 청산 (Reversal Early Exit) (`src/strategy.py`)
단일 폭을 기준 삼는 익절 로직만으로는 과매수/과매도 구간에서 급락하는 변곡점에 대응하기 어려웠습니다. 상승 모멘텀 고갈을 포착하기 위해 자금 흐름 지표(Money Flow Index)의 극단값과 가격 추세의 이탈(Divergence)이 겹치는 시그널을 구조화하였고, 시그널 관측 시 즉각 탈출하는 동적 리스크 관리 기능을 추가하여 변동성 위험을 해소했습니다.

### 4. 하드 스탑 방어 (Flash Crash Protection) (`src/execution.py`)
거래소 API 호출에만 의존하는 소프트 스탑로스(Soft Stop-loss)는 로컬 클라우드 봇 지연이나 급락장(Flash Crash)에서의 거래소 통신 병목 시 주문이 누락될 리스크가 치명적이었습니다. 진입과 동시에 거래소 매칭 엔진 서버에 트리거를 직접 박아넣는 하드 스탑로스(Hard Stop-Loss, `STOP_MARKET`)를 자동 발주하는 이중 안전 시스템을 구축하였고, `closePosition: True` 옵션 매개변수로 수량 잔여 오차 위험까지 원천 차단했습니다.

### 5. Live-Simulation 및 Deep Warm-up 아키텍처 (`src/data_loader.py`)
봇 배포 직후 실시간 API만으로 장기 지표(예: 100주기 이상)를 추산할 시, 초기 캔들 누락으로 필드 연산(Cold Start) 지연 릴리즈 한계가 존재했습니다. 이를 극복하기 위해 로컬의 과거 N년 치 캐시 데이터(Pickle) 파일 풀과 최신화된 실시간 호가 API를 결합 후 무결하게 병합(Merge & Deduplicate)하는 데이터 파이프라인을 구축하여 봇 가동 즉시 지표 산출과 거래망 참여를 달성했습니다.

### 6. 그리드 서치 (Grid Search) 및 가상 원장(Paper Trading) 시스템 (`research/optimizer.py`, `src/execution.py`)
단일 모델의 최고 PnL 수치에 매몰될 경우 발생하는 심각한 과최적화(Curve-fitting) 모래성 붕괴 현상을 방지하고자, `joblib` 연산 코어 베이스의 **결정적 Grid Search 툴**을 내부 개발하여 파라미터 유니버스를 전수 조사했습니다. 또한, 검증된 변수를 실환경에 투입하기 전 논리적 오류로 인한 자본 손실을 막기 위해 API 체결망만 차단하고 가상 원장(In-Memory Ledger)을 업데이트하는 핫스왑(Hot-swap) 방식의 Paper Trading 엔진을 구현하여 알고리즘 전진 분석망을 완성했습니다.
