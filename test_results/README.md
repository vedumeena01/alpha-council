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
| **05** | Trading Psychology, Wick-to-Wick & Anti-News Engine | 5 | **100%** (5/5) | 0.14s | Base Candle Count Scorer (1-3 vs 4-5+), Wick-to-Wick Marking, Direct Reversals (0 Base), Timeframe Hierarchy (Monthly 4.0x), News Trap Contrarian Filter | [`EPISODE_05_TEST_RESULTS.md`](EPISODE_05_TEST_RESULTS.md) |
| **06** | Price Action Behind Candles (Closing, Gap-Base, Garbage) | 6 | **100%** (6/6) | 0.15s | The Closing Concept (Proven vs. Unproven), Gap+Base Exciting Equation, LOTL Stacking, Garbage Area Filter, Origin Pivot Isolation | [`EPISODE_06_TEST_RESULTS.md`](EPISODE_06_TEST_RESULTS.md) |
| **07** | Multiple Time Frame Analysis (MTFA, 50 SMA Clock, Boundary Rule) | 5 | **100%** (5/5) | 0.23s | 50 SMA Clock Method (7th Candle Rule), 5 Curve Sections, Curve vs. Trend Matrix, The Boundary Rule, ATH Shorting Prohibition | [`EPISODE_07_TEST_RESULTS.md`](EPISODE_07_TEST_RESULTS.md) |
| **Total** | **All Episodes (Cumulative)** | **29** | **100%** (29/29) | **0.25s** | **Full GTF Price Action Core (`zone_engine.py`)** | - |

---

## 🔬 System Health & Test Coverage Progress

```text
Module: alphacouncil/alpha/zone_engine.py
Statements: 529
Missed: 71
Test Coverage: 86.6%
Total Suite Tests: 48 (100% Passed)
Linter Status: Ruff 0 errors, 0 warnings
CI Status: GitHub Actions 100% Green (Python 3.11 & 3.12)
```

---

## 🗂️ File Directory
- [`EPISODE_01_TEST_RESULTS.md`](EPISODE_01_TEST_RESULTS.md) - Session partitions & candle anatomy.
- [`EPISODE_02_TEST_RESULTS.md`](EPISODE_02_TEST_RESULTS.md) - 50% candle classification.
- [`EPISODE_03_TEST_RESULTS.md`](EPISODE_03_TEST_RESULTS.md) - Zone marking & freshness.
- [`EPISODE_04_TEST_RESULTS.md`](EPISODE_04_TEST_RESULTS.md) - Exceptional marking & trade execution.
- [`EPISODE_05_TEST_RESULTS.md`](EPISODE_05_TEST_RESULTS.md) - Trading psychology, wick-to-wick, direct reversals & news traps.
- [`EPISODE_06_TEST_RESULTS.md`](EPISODE_06_TEST_RESULTS.md) - The Closing concept, Gap+Base exciting, LOTL stacking, origin pivot & garbage filter.
- [`EPISODE_07_TEST_RESULTS.md`](EPISODE_07_TEST_RESULTS.md) - Multiple Time Frame Analysis (MTFA), 50 SMA clock method, 5 curve tiers & boundary rule.
