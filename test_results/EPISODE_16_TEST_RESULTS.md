# 📊 Test Results: Episode 16
> **Episode Title:** Sectoral Analysis & The Confluence Multiplier (+2 Supreme Add-on)  
> **Source Modules:** `alphacouncil/alpha/sector_engine.py`, `alphacouncil/alpha/zone_engine.py`  
> **Test File:** `tests/test_zone_engine.py`  
> **Status:** ✅ **100% PASSED**  
> **Execution Timestamp:** 2026-11-18 20:05 IST

---

## 1. Test Command & Execution Output
```bash
pytest -v tests/test_zone_engine.py -k "episode_16"
```

```text
============================= test session starts =============================
platform win32 -- Python 3.13.13, pytest-9.1.1, pluggy-1.7.0 -- C:\Python313\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\vedpr\OneDrive\Desktop\alpha-council
configfile: pyproject.toml
plugins: anyio-4.14.2, platformdirs-4.13.5, cov-7.1.0
collecting ... collected 75 items / 69 deselected / 6 selected

tests/test_zone_engine.py::test_episode_16_sector_support_plus_two_bonus_trade_score PASSED [ 16%]
tests/test_zone_engine.py::test_episode_16_the_missing_support_filter_blocks_long_execution PASSED [ 33%]
tests/test_zone_engine.py::test_episode_16_simultaneous_triad_alignment_level_3_rocket_move_sbi_case_study PASSED [ 50%]
tests/test_zone_engine.py::test_episode_16_heavyweight_concentration_greater_than_50_percent_rule PASSED [ 66%]
tests/test_zone_engine.py::test_episode_16_sector_rotation_dynamics_sectors_cannot_go_to_zero PASSED [ 83%]
tests/test_zone_engine.py::test_episode_16_portfolio_construction_12_to_15_stocks_and_sector_allocation PASSED [100%]

====================== 6 passed, 69 deselected in 0.38s =======================
```

---

## 2. Capabilities Tested & Verified

| Feature / Concept | Test Function | Input / Scenario | Assertion & Outcome |
| :--- | :--- | :--- | :--- |
| **+2 Supreme Sector Support Add-on** | `test_episode_16_sector_support_plus_two_bonus_trade_score` | Ordinary 6.0/7.0 stock demand setup (Freshness 3, Strength 1, Time at Base 2); parent sector hits Demand Zone | Awards **+2.0 Extra Trade Score Points**, elevating setup from ordinary 6.0 to **8.0 / 7.0**; top-down auditor confirms setup approval with sector tailwind. |
| **The Missing Support Filter** | `test_episode_16_the_missing_support_filter_blocks_long_execution` | Stock in Demand Zone, but parent sector is in free fall towards lower demand | `evaluate_simultaneous_confluence` flags `MISSING_SUPPORT` warning; top-down auditor blocks long execution with "The Missing Support Trap Detected" to preserve capital. |
| **Level 3 Triad Alignment (Rocket Move)** | `test_episode_16_simultaneous_triad_alignment_level_3_rocket_move_sbi_case_study` | Feb 29, 2016 Case Study: SBI in Monthly DZ + Bank Nifty in Monthly DZ + Nifty 50 at 6,800 Monthly DZ simultaneously | Declares `LEVEL_3_ROCKET_MOVE`; confirms `is_rocket_move = True`; awards +2.0 points; validates exponential upside momentum regardless of external headlines. |
| **>50% Heavyweight Concentration Rule** | `test_episode_16_heavyweight_concentration_greater_than_50_percent_rule` | Nifty Auto (M&M 20%, Maruti 19%, Tata Motors 12% = 51.0%) vs. Nifty Metal with heavyweights in supply & SAIL (4%) in demand | Accurately identifies bullish index propel when heavyweights (>50%) are in Demand; proves low-weight constituent jumps cannot lift sector if heavyweights face supply drag. |
| **Sector Rotation Dynamics ("Sectors Cannot Go to Zero")** | `test_episode_16_sector_rotation_dynamics_sectors_cannot_go_to_zero` | Nifty PSU Bank at macro demand origin with 3 tested supply zones vs. Sector at All-Time High | Identifies `ACCUMULATION_AT_CYCLE_LOW` and exhausted supply trendlines clearing runway; triggers `PEAK_AT_ALL_TIME_HIGH` with advisory to rotate into lagging constituents (GTF 40-40-20 rule). |
| **Portfolio Construction (12-15 Stocks & 2-4 per Sector)** | `test_episode_16_portfolio_construction_12_to_15_stocks_and_sector_allocation` | 14 stocks across 5 sectors (2-3 per sector) vs. 8 stocks (<12) vs. 17 stocks (>15) vs. 5 Banks in single sector (>4) | Approves optimal 14-stock allocation; rejects under-diversification (<12), index-like dilution (>15), and single-sector over-concentration (>4). |

---

## 3. Full Test Suite & Coverage Integration

```text
=============================== tests coverage ================================
Name                                  Stmts   Miss  Cover
---------------------------------------------------------
alphacouncil\alpha\sector_engine.py     144     14    90%
alphacouncil\alpha\zone_engine.py      1193    188    84%
alphacouncil\risk\gtf_risk.py           132      6    95%
---------------------------------------------------------
TOTAL                                  1469    208    86%
============================= 94 passed in 0.80s ==============================
```
- **Cumulative Zone, Sector & Risk Tests:** 75 tests
- **Cumulative Total Suite Tests:** 94 tests
- **Pass Rate:** 100%
- **Linter Status:** Ruff 100% Clean (`All checks passed!`)
