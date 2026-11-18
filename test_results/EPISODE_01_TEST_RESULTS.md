# 📊 Test Results: Episode 1
> **Episode Title:** Best Charting Software & Candlestick Anatomy  
> **Source Module:** `alphacouncil/alpha/zone_engine.py`  
> **Test File:** `tests/test_zone_engine.py`  
> **Status:** ✅ **100% PASSED**  
> **Execution Timestamp:** 2026-11-18 17:10 IST

---

## 1. Test Command & Execution Output
```bash
pytest -v tests/test_zone_engine.py -k "episode_01"
```

```text
============================= test session starts =============================
platform win32 -- Python 3.13.13, pytest-9.1.1, pluggy-1.7.0 -- C:\Python313\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\vedpr\OneDrive\Desktop\alpha-council
configfile: pyproject.toml
plugins: anyio-4.14.2, platformdirs-4.13.5, cov-7.1.0
collecting ... collected 13 items / 11 deselected / 2 selected

tests/test_zone_engine.py::test_episode_01_nse_session_partitions_no_orphan_candles PASSED [ 50%]
tests/test_zone_engine.py::test_episode_01_wickless_candles_directional_power PASSED [100%]

====================== 2 passed, 11 deselected in 0.14s =======================
```

---

## 2. Capabilities Tested & Verified

| Feature / Concept | Test Function | Input / Scenario | Assertion & Outcome |
| :--- | :--- | :--- | :--- |
| **NSE Session Partitions** | `test_episode_01_nse_session_partitions_no_orphan_candles` | 375-minute Indian market trading hours (09:15 - 15:30 IST) | `375 % 75 == 0` (5 bars/day), `375 % 125 == 0` (3 bars/day). Zero distorted orphan bars. |
| **Wickless Green Candle** | `test_episode_01_wickless_candles_directional_power` | `Open == Low` (100.0, Close 114.0) | `OPEN_EQUALS_LOW_PURE_BUYING`: Zero lower shadow confirms pure institutional accumulation. |
| **Wickless Red Candle** | `test_episode_01_wickless_candles_directional_power` | `Open == High` (150.0, Close 132.0) | `OPEN_EQUALS_HIGH_PURE_SELLING`: Zero upper shadow confirms pure aggressive dumping. |

---

## 3. Quantitative Performance
- **Tests Run:** 2
- **Pass Rate:** 100% (2 Passed, 0 Failed, 0 Skipped)
- **Execution Latency:** 0.14 seconds
- **Linter Status:** Ruff Clean (0 errors)
