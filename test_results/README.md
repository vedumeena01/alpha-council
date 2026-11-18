# 🏛️ AlphaCouncil: Episode Test Results & Comparison Matrix
> **Master Registry:** Automated empirical test results tracking each episode of *Trading in the Zone*.  
> **Purpose:** Compare test coverage, validation accuracy, and rule verification across the training curriculum.

---

## 📈 Episode Comparison Matrix

| Ep # | Episode Title | Tests Count | Pass Rate | Test Latency | Tested Algorithms & Principles | Detailed Report |
| :---: | :--- | :---: | :---: | :---: | :--- | :---: |
| **01** | Best Charting Software & Candlestick Anatomy | 2 | **100%** (2/2) | 0.14s | 375m NSE Session Partition (75m, 125m), Wickless Candles ($O=L, O=H$) | [`EPISODE_01_TEST_RESULTS.md`](EPISODE_01_TEST_RESULTS.md) |
| **02** | Why Does Stock Price Go Up and Down? | 1 | **100%** (1/1) | 0.15s | 50% Body-to-Range Rule, Green/Red Exciting vs. Base Candle Classification | [`EPISODE_02_TEST_RESULTS.md`](EPISODE_02_TEST_RESULTS.md) |
| **03** | Demand & Supply Zone Marking & Freshness | 4 | **100%** (4/4) | 0.14s | Proximal/Distal Line Placement, 4 Patterns (DBR, RBR, RBD, DBD), Fresh vs. Tested, CMP Navigation | [`EPISODE_03_TEST_RESULTS.md`](EPISODE_03_TEST_RESULTS.md) |
| **04** | Entry, Stoploss, Target & Exceptional Marking | 6 | **100%** (6/6) | 0.14s | Proximal Invariance, Reversal 3-Wick Rule, Continuous Leg-in Exclusion, Speeding Bus SL Buffer, 2:1 Target | [`EPISODE_04_TEST_RESULTS.md`](EPISODE_04_TEST_RESULTS.md) |
| **Total** | **All Episodes (Cumulative)** | **13** | **100%** (13/13) | **0.17s** | **Full GTF Price Action Core (`zone_engine.py`)** | - |

---

## 🔬 System Health & Test Coverage Progress

```text
Module: alphacouncil/alpha/zone_engine.py
Statements: 187
Missed: 11
Test Coverage: 94.1%
Linter Status: Ruff 0 errors, 0 warnings
CI Status: GitHub Actions 100% Green (Python 3.11 & 3.12)
```

---

## 🗂️ File Directory
- [`EPISODE_01_TEST_RESULTS.md`](EPISODE_01_TEST_RESULTS.md) - Session partitions & candle anatomy.
- [`EPISODE_02_TEST_RESULTS.md`](EPISODE_02_TEST_RESULTS.md) - 50% candle classification.
- [`EPISODE_03_TEST_RESULTS.md`](EPISODE_03_TEST_RESULTS.md) - Zone marking & freshness.
- [`EPISODE_04_TEST_RESULTS.md`](EPISODE_04_TEST_RESULTS.md) - Exceptional marking & trade execution.
