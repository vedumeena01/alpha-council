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
| **08** | Trade Score, Mahabharata Alignment & Dynamic Target | 5 | **100%** (5/5) | 0.38s | Trade Score (Max 7/7), 4 Characters (Krishna, Bhishma, Arjuna, Duryodhana), Opposing ITF Target Rule, Best Setup Gold Standard | [`EPISODE_08_TEST_RESULTS.md`](EPISODE_08_TEST_RESULTS.md) |
| **09** | Trading Style, Authentic Zones & The Rejection Mindset | 5 | **100%** (5/5) | 0.25s | Entry Types (Set & Forget vs. Type 2 In-Zone), Zone Authenticity & Retest Vulnerability, Rupee-Risk Equality, Mandatory 100-Trade Rule, Rejection Mindset Audit | [`EPISODE_09_TEST_RESULTS.md`](EPISODE_09_TEST_RESULTS.md) |
| **10** | Risk Management, Position Sizing & Anti-Tamper Discipline | 5 | **100%** (5/5) | 0.28s | Exact Position Sizing ($Qty = \lfloor RPT / |Entry - SL| \rfloor$), Monetary Risk Invariance, Anti-Tamper Guards (Widening, Averaging, Chasing), 10 Trades/Month Cap, 40-Mistake Elimination, Excel Growth Model, HTF Overpowering | [`EPISODE_10_TEST_RESULTS.md`](EPISODE_10_TEST_RESULTS.md) |
| **11** | When to be Aggressive vs. Conservative (Execution Stances) | 5 | **100%** (5/5) | 0.28s | Aggressive vs. Conservative Stance Selector, The Matching Timeframe Principle, The Steamroller Effect, Proven Achievement Rule, Anchoring SL to Shri Krishna, TVS Motor Regime Inversion, Dynamic 20 EMA Interaction | [`EPISODE_11_TEST_RESULTS.md`](EPISODE_11_TEST_RESULTS.md) |
| **Total** | **All Episodes (Cumulative)** | **49** | **100%** (49/49) | **0.53s** | **Full GTF Price Action, Risk & Dynamic Execution Architecture (`zone_engine.py` + `gtf_risk.py`)** | - |

---

## 🔬 System Health & Test Coverage Progress

```text
Modules: alphacouncil/alpha/zone_engine.py + alphacouncil/risk/gtf_risk.py
Zone Engine Statements: 838 (Coverage: 84%)
GTF Risk Statements: 132 (Coverage: 95%)
Total Suite Tests: 68 (100% Passed)
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
- [`EPISODE_08_TEST_RESULTS.md`](EPISODE_08_TEST_RESULTS.md) - Trade Score (7/7), Mahabharata Alignment, Dynamic Opposing ITF Target & Best Setup Gold Standard.
- [`EPISODE_09_TEST_RESULTS.md`](EPISODE_09_TEST_RESULTS.md) - Trading Style, Authentic Zones, Rupee-Risk Equality, 100-Trade Directive & Rejection Mindset.
- [`EPISODE_10_TEST_RESULTS.md`](EPISODE_10_TEST_RESULTS.md) - Risk Management, Position Sizing, Anti-Tamper Guards, 10 Trades/Month Cap & Excel Growth Models.
- [`EPISODE_11_TEST_RESULTS.md`](EPISODE_11_TEST_RESULTS.md) - Aggressive vs. Conservative Execution Stances, The Steamroller Effect, The Matching Timeframe Principle, Macro Anchoring to Shri Krishna & Regime Inversion.
