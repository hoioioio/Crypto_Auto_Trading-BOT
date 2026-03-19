# 📈 Crypto_Auto_Trading-BOT (KAMA-Based Systematic Trend Following Engine)

[🚀 View Interactive Backtest Dashboard](https://hoioioio.github.io/Crypto_Auto_Trading-BOT/)

This project is a **data-driven systematic trading engine** targeting the Binance Futures market. It generates a stable, upward-sloping equity curve by employing an **Adaptive Moving Average (KAMA)** that dynamically adjusts signal responsiveness based on market volatility regimes, combined with a **3-Stage Pyramiding (Scaling-in)** execution logic to maximize Risk/Reward asymmetry.

---

## 🏦 6-Year Institutional-Grade Backtest Performance (2020.01 - 2026.03)
This project rejects naive curve-fitting. The performance metrics presented below are the result of rigorous quantitative reality checks and institutional constraints.

### 🛡️ Institutional Constraints Applied
1. **Liquidity Hard Cap:** To realistically model the slippage that occurs when scaling position sizes, a **strict $100,000 maximum notional cap per entry** constraint is enforced.
2. **Transaction Cost Analysis (TCA) Integration:** The chronic weakness of long-term trend following—funding rates—is fully accounted for. A **-0.01% penalty is permanently deducted every 8 hours** in the backtest PnL to simulate real-world carry costs.
3. **Walk-Forward Analysis (WFA):** The optimal risk allocation (`1.25% fractional Kelly sizing`) was derived strictly from historical in-sample data (2020-2023). This parameter was then locked, and the system was subjected to a blind Out-of-Sample (OOS) test (2024-2026) to prevent overfitting.
4. **Monte Carlo Sequence Risk:** The chronological sequence of the 1,580+ live-simulated trades over 6 years was randomly shuffled **10,000 times**. Analysis proves that even at the 99% confidence interval (worst-case black swan sequence), the Maximum Drawdown (MDD) is mathematically contained below 43%.

---

### 📊 Performance Metrics (Post-Penalty)
* **Trading Universe:** DOGE, LUNA2, SOL, ZEC, ETH, BNB, AVAX (BTC Excluded to maximize Altcoin Beta)
* **Initial Capital:** $1,000

| Metric | Value | Note |
| :--- | :--- | :--- |
| **Net Profit** | **+181,650.6%** | $1,000 → $1,817,506 (1,817x ROI) |
| **Max Drawdown (MDD)** | **28.45%** | Robust downside protection including all hard caps & funding penalties. |
| **Sortino Ratio** | **12.194** | Exceptional return efficiency against downside volatility. |
| **Sharpe Ratio** | **1.165** | High statistical edge relative to aggressive compounding variance. |
| **Profit Factor** | **1.689** | Gross Profit is 1.68x Gross Loss. |
| **Win Rate** | **27.26%** | Asymmetric R:R - 'Cut losses precisely, let profits run exponentially.' |

> Achieving a **Sortino Ratio of 12.19** with a 27.26% win rate is the mathematical footprint of the scaling-in (Pyramiding) architecture, which compounds profitability during massive momentum expansion while KAMA tightly cuts losses during choppy, mean-reverting regimes. 
The tightly controlled 28.45% MDD is the direct result of the **1.25% Realized Equity Fractional Sizing**, ensuring the portfolio survives catastrophic market drawdowns without risking ruin.

![Strategy Equity vs Bitcoin Benchmark](benchmark_chart.png)

### 💎 Stress Test Metrics (Fat-Tail Risk Assessment)
Beyond cumulative metrics, the system has passed multidimensional stress tests regarding tail-risk events.

| Metric | Result | Benchmark (BTC) | Note |
| :--- | :--- | :--- | :--- |
| **Stress Test 1** <br>*(2022 LUNA/FTX Crash)* | **MDD 16.51%**<br>*(Period PnL: -8.84%)* | **76.63% Drop** | Survived the worst crypto winter via Short positioning & KAMA regime detection. |
| **Stress Test 2** <br>*(2025.10 Market Crash)* | **MDD 4.70%**<br>*(Period PnL: -4.11%)* | **14.62% Drop** | Near-perfect defense by pre-emptively flattening risk exposure before the crash. |
| **Stress Test 3** <br>*(Early 2026 Flash Crash)* | **MDD 10.99%**<br>*(Period PnL: +18.00%)* | **35.11% Drop** | Generated a **+18% net profit (Long/Short switching)** while the broader market collapsed by 35%. |
| **Rolling MDD** <br>*(Random 6-Month Holding)* | **Avg 26.4%** | N/A | Definitively proves lack of chronological overfitting. Catastrophic liquidation is prevented regardless of the start month. |

---

## 🛠️ Tech Stack
* **Language**: Python 3.x
* **Core Libraries**: Pandas, NumPy (Vectorized operations), CCXT, Joblib
* **Infrastructure**: Real-time Telegram API Telemetry & Watchdog Monitoring

---

## 📁 Project Architecture

* 📁 **`src/`**
  * 📄 `indicators.py` - Custom mathematically formulated Indicators (AWMA, KAMA) without external dependencies.
  * 📄 `strategy.py` - Core Alpha layer: Dynamic Scaling & Reversal Early Exit Logic.
  * 📄 `execution.py` - Execution layer: CCXT Order Wrapper, Hard SL injection, Paper Trading engine.
  * 📄 `data_loader.py` - In-Memory processing & History vs Live Data Sync Pipeline.
* 📁 **`research/`**
  * 📄 `optimizer.py` - Multi-core Grid Search Parameter Optimizer targeting Robust Plateaus.
  * 📄 `backtester.py` - Walk-forward simulation engine with TCA.
* 📁 **`config/`**
  * 📄 `settings.yaml` - Model hyper-parameters, sizing rules, and leverage thresholds.
* 📄 `main.py` - 24/365 Event Loop & Production Daemon.

---

## 🔩 Core Engineering Highlights (7 Pillars)

This project was built from scratch using first-principles to bridge the gap between backtest theory and production reality.

### 1. Vectorized Adaptive Weighted Moving Average (KAMA) (`src/indicators.py`)
* **🚨 The Problem:** Standard SMAs/EMAs suffer from inherent 'lag', triggering chronic whipsaw losses during ranging markets.
* **💡 The Solution:** Instead of relying on static-period `TA-Lib` functions, I engineered Kaufman's Adaptive Moving Average (KAMA) purely in Python/NumPy. The algorithm dynamically calculates the market's **Efficiency Ratio (ER)** (Directional Movement / Absolute Volatility).
* **🎯 Result:** The moving average flattens out during noisy, low-efficiency regimes (preventing false breakouts) and sharply accelerates its smoothing constant during high-efficiency trends.

### 2. 3-Stage Conditional Pyramiding (Scaling in) (`src/strategy.py`)
* **🚨 The Problem:** Deterministic 'All-in' entry models expose maximum capital during the highest-uncertainty phase (the breakout threshold).
* **💡 The Solution:** Engineered a Conditional Scaling-in algorithm. The system takes a 'probe' entry. Only when mathematical safety margins (positive Unrealized PnL) are secured, the system injects Stage 2 (30%) and Stage 3 (40%) tranches.
* **🎯 Result:** Drastically reduces the capital impact of false breakouts while exponentially compounding exposure during confirmed momentum anomalies.

### 3. Reversal Early Exit via Market Regime Detection (`src/strategy.py`)
* **🚨 The Problem:** Static %-based trailing stops are blind to thermodynamic market exhaustion (overbought/oversold extremes).
* **💡 The Solution:** Implemented a 'Reversal Hunter' module. By continuously correlating extreme Money Flow Index (MFI) values with short-term price divergence from fast MAs, the system detects liquidity exhaustion.
* **🎯 Result:** The system preemptively flattens the portfolio via market orders *before* mean-reversion pullbacks obliterate accumulated unrealized gains.

### 4. Flash Crash Protection Architecture (Hard Stops) (`src/execution.py`)
* **🚨 The Problem:** Software-based stop-losses operating via REST API loops are completely useless during exchange downtime, WebSocket disconnects, or systemic flash crashes.
* **💡 The Solution:** Delegated critical risk management directly to the Exchange's Matching Engine. Upon position entry, the bot immediately dispatches a `STOP_MARKET` order pegged to the `MARK_PRICE` to Binance's servers with the `closePosition: True` flag to prevent precision residue.
* **🎯 Result:** Even if the cloud server hosting the bot is physically destroyed, the portfolio is mathematically guaranteed to liquidate exactly at the 1.25% risk threshold.

### 5. Deep Warm-up & In-Memory Sync Architecture (`src/data_loader.py`)
* **🚨 The Problem:** Relying purely on live API calls causes historical indicator 'cold-start' latency (e.g., waiting 100 periods to calculate a 100-MA).
* **💡 The Solution:** Designed a hybrid data pipeline that continuously serializes historical exchange data to a local File/Pickle cache. On boot, the engine instantly loads years of history into memory and merges it with real-time `fetch_ohlcv` payloads, performing automated deduplication.
* **🎯 Result:** Zero-latency indicator calculation upon restart and zero deviation between backtest data integrity and production ingestion.

### 6. Robust Plateau Grid Search Optimization (`research/optimizer.py`)
* **🚨 The Problem:** Standard backtesters fall victim to curve-fitting by isolating the single parameter combination with the highest historical PnL, which inevitably collapses out-of-sample.
* **💡 The Solution:** Built a multidimensional, multi-core `joblib` grid search engine. Instead of optimizing for PnL, the fitness function solves for **Robustness**. The algorithm penalizes sharp parameter peaks and searches exclusively for broad, flat, stable topological parameter landscapes where minor variations do not destroy the Sharpe ratio.
* **🎯 Result:** Parameters are stress-tested against variance, yielding a configuration built for true out-of-sample survival rather than historical data mining.

### 7. Virtual Paper Trading & Latency Mapping (`src/execution.py`)
* **🚨 The Problem:** Deploying untested alpha architectures directly to the production matching engine carries unacceptable monetary execution risk.
* **💡 The Solution:** Engineered a hot-swappable Virtual Ledger (`LIVE_MODE = False`). The system ingests identical production market data but intercepts the execution layer. It mathematically simulates Taker Fees, Bid/Ask spread crossing, and tick-level slippage internally.
* **🎯 Result:** Allows completely risk-free Forward-Testing of the algorithm in a live market environment with institutional accuracy before flipping the switch to live capital allocation.
