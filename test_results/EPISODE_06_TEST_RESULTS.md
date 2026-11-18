# 📊 Test Results: Episode 6
> **Episode Title:** Price Action Behind the Candles (Closing, Gap-Base, Garbage Areas & Origins)  
> **Source Module:** `alphacouncil/alpha/zone_engine.py`  
> **Test File:** `tests/test_zone_engine.py`  
> **Status:** ✅ **100% PASSED**  
> **Execution Timestamp:** 2026-11-18 17:40 IST

---

## 1. Test Command & Execution Output
```bash
pytest -v tests/test_zone_engine.py -k "episode_06"
```

```text
============================= test session starts =============================
platform win32 -- Python 3.13.13, pytest-9.1.1, pluggy-1.7.0 -- C:\Python313\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\vedpr\OneDrive\Desktop\alpha-council
configfile: pyproject.toml
plugins: anyio-4.14.2, platformdirs-4.13.5, cov-7.1.0
collecting ... collected 24 items / 18 deselected / 6 selected

tests/test_zone_engine.py::test_episode_06_closing_concept_demand PASSED [ 16%]
tests/test_zone_engine.py::test_episode_06_closing_concept_supply PASSED [ 33%]
tests/test_zone_engine.py::test_episode_06_gap_plus_base_equals_exciting_candle PASSED [ 50%]
tests/test_zone_engine.py::test_episode_06_level_on_top_of_level_lotl PASSED [ 66%]
tests/test_zone_engine.py::test_episode_06_garbage_area_filtering PASSED [ 83%]
tests/test_zone_engine.py::test_episode_06_origin_pivot_isolation PASSED [100%]

====================== 6 passed, 18 deselected in 0.15s =======================
```

---

## 2. Capabilities Tested & Verified

| Feature / Concept | Test Function | Input / Scenario | Assertion & Outcome |
| :--- | :--- | :--- | :--- |
| **Closing Concept (Demand)** | `test_episode_06_closing_concept_demand` | Proven zone (Close 124 > High 121) vs. Unproven zone (Close 118 < High 135) | Proven zone: `has_clean_closing == True`, `is_proven_zone == True`. Unproven zone penalized with `is_high_quality == False` and strength reduced (overhead supply active). |
| **Closing Concept (Supply)** | `test_episode_06_closing_concept_supply` | Proven zone (Close 95 < Low 99) vs. Unproven zone (Close 100 > Low 85) | Proven zone confirms buyers neutralized. Unproven zone flags persistent underlying demand risk. |
| **Gap + Base = Exciting Candle** | `test_episode_06_gap_plus_base_equals_exciting_candle` | Overnight gap up from 100 to 105, daytime range 0.7 (Base candle intraday) | Classified as `GREEN_EXCITING` (`is_gap_exciting == True`). Captures institutional pre-market buying footprint. |
| **Level-on-Top-of-Level (LOTL)** | `test_episode_06_level_on_top_of_level_lotl` | Stacked demand zones: Zone 1 (Origin) & Zone 2 (Gap-Base cushion) | Detected stacked pair. Confirms Zone 2 acts as absorption cushion protecting Zone 1. |
| **Garbage Area Filtering** | `test_episode_06_garbage_area_filtering` | 7-bar directionless congestion band with overlapping wicks | Identified as `is_garbage_cluster == True`. Suppresses low-probability forced zones inside noise. |
| **Origin Pivot Isolation** | `test_episode_06_origin_pivot_isolation` | 4 base candle cluster where 2nd basing bar had extreme low (101.0) | `origin_candle_idx == 2`. Accurately isolates true institutional launch pivot, eliminating inflated stop-loss width. |

---

## 3. Quantitative Performance
- **Tests Run:** 6 (Cumulative Zone Engine Tests: 24)
- **Pass Rate:** 100% (6 Passed, 0 Failed, 0 Skipped)
- **Execution Latency:** 0.15 seconds
- **Linter Status:** Ruff Clean (0 errors)
