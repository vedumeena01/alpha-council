# 📊 Test Results: Episode 5
> **Episode Title:** Trading Psychology | Your Mind vs News | Trading in the Zone  
> **Source Module:** `alphacouncil/alpha/zone_engine.py`  
> **Test File:** `tests/test_zone_engine.py`  
> **Status:** ✅ **100% PASSED**  
> **Execution Timestamp:** 2026-11-18 17:28 IST

---

## 1. Test Command & Execution Output
```bash
pytest -v tests/test_zone_engine.py -k "episode_05"
```

```text
============================= test session starts =============================
platform win32 -- Python 3.13.13, pytest-9.1.1, pluggy-1.7.0 -- C:\Python313\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\vedpr\OneDrive\Desktop\alpha-council
configfile: pyproject.toml
plugins: anyio-4.14.2, platformdirs-4.13.5, cov-7.1.0
collecting ... collected 18 items / 13 deselected / 5 selected

tests/test_zone_engine.py::test_episode_05_zone_strength_base_candle_count PASSED [ 20%]
tests/test_zone_engine.py::test_episode_05_wick_to_wick_marking PASSED   [ 40%]
tests/test_zone_engine.py::test_episode_05_direct_reversal_missing_base_candles PASSED [ 60%]
tests/test_zone_engine.py::test_episode_05_timeframe_hierarchy_dominance PASSED [ 80%]
tests/test_zone_engine.py::test_episode_05_psychology_news_trap_evaluation PASSED [100%]

====================== 5 passed, 13 deselected in 0.14s =======================
```

---

## 2. Capabilities Tested & Verified

| Feature / Concept | Test Function | Input / Scenario | Assertion & Outcome |
| :--- | :--- | :--- | :--- |
| **Zone Strength by Base Count** | `test_episode_05_zone_strength_base_candle_count` | Setup A (1 Base Candle) vs. Setup B (4 Base Candles) | Setup A: `HIGH_STRENGTH` (Score 1.0, quick victory); Setup B: `MODERATE_STRENGTH` (Score 0.6, prolonged struggle). |
| **Wick-to-Wick Marking** | `test_episode_05_wick_to_wick_marking` | Demand base (High 109, Low 101, Max Body 107); Supply base (High 118, Low 111, Min Body 113) | Demand Wick-to-Wick PL shifts to 109.0 (highest wick); Supply Wick-to-Wick PL shifts to 111.0 (lowest wick). Prevents missed entries in explosive setups. |
| **Direct Reversals (0 Base)** | `test_episode_05_direct_reversal_missing_base_candles` | Red drop immediately followed by Green rally without basing bar | `is_direct_reversal == True`, `base_candles_count == 0`, PL = 100.0 (reversal interface body), DL = 96.0 (extreme wick). |
| **Timeframe Hierarchy** | `test_episode_05_timeframe_hierarchy_dominance` | Monthly vs. Daily vs. Intraday zone comparison | `Monthly (4.0x) > Weekly (3.0x) > Daily (2.0x) > Intraday (1.0x)`. Monthly zones backed by institutional block capital dominate. |
| **Trading Psychology & News Traps** | `test_episode_05_psychology_news_trap_evaluation` | Axis Bank / Maggi ban (-0.85 sentiment into Demand) vs. HDFC Merger (+0.90 sentiment into Supply) | Negative news + Demand $\to$ `RETAIL_PANIC_LIQUIDITY_TRAP` (Accumulate with institutions). Euphoria news + Supply $\to$ `RETAIL_EUPHORIA_LIQUIDITY_TRAP` (Distribute/Short). *"Human can lie, but chart can't."* |

---

## 3. Quantitative Performance
- **Tests Run:** 5 (Cumulative Zone Engine Tests: 18)
- **Pass Rate:** 100% (5 Passed, 0 Failed, 0 Skipped)
- **Execution Latency:** 0.14 seconds
- **Linter Status:** Ruff Clean (0 errors)
