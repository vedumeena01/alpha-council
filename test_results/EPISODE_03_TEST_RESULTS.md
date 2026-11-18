# 📊 Test Results: Episode 3
> **Episode Title:** Demand & Supply Zone Marking & Freshness Engine  
> **Source Module:** `alphacouncil/alpha/zone_engine.py`  
> **Test File:** `tests/test_zone_engine.py`  
> **Status:** ✅ **100% PASSED**  
> **Execution Timestamp:** 2026-11-18 17:10 IST

---

## 1. Test Command & Execution Output
```bash
pytest -v tests/test_zone_engine.py -k "demand_zone_marking or tested_zone or supply_zone_marking or active_zones"
```

```text
============================= test session starts =============================
platform win32 -- Python 3.13.13, pytest-9.1.1, pluggy-1.7.0 -- C:\Python313\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\vedpr\OneDrive\Desktop\alpha-council
configfile: pyproject.toml
plugins: anyio-4.14.2, platformdirs-4.13.5, cov-7.1.0
collecting ... collected 13 items / 9 deselected / 4 selected

tests/test_zone_engine.py::test_demand_zone_marking_and_freshness PASSED [ 25%]
tests/test_zone_engine.py::test_tested_zone_detection PASSED             [ 50%]
tests/test_zone_engine.py::test_supply_zone_marking PASSED               [ 75%]
tests/test_zone_engine.py::test_find_active_zones_relative_to_cmp PASSED [100%]

======================= 4 passed, 9 deselected in 0.14s =======================
```

---

## 2. Capabilities Tested & Verified

| Feature / Concept | Test Function | Input / Scenario | Assertion & Outcome |
| :--- | :--- | :--- | :--- |
| **Demand Zone Marking** | `test_demand_zone_marking_and_freshness` | DBR formation (Red drop -> Base -> Green rally) | Proximal Line = 107.0 (Highest body of base), Distal Line = 101.0 (Lowest wick of base), Zone Width = 6.0. |
| **Zone Freshness** | `test_demand_zone_marking_and_freshness` | Subsequent price candles trade strictly above 107.0 | `is_fresh == True`. Pending institutional buy orders remain untouched. |
| **Tested Zone Detection** | `test_tested_zone_detection` | Subsequent bar retests zone dipping to low 106.0 ($\le 107.0$) | `is_fresh == False`, `tested_at_idx == 3`. Zone marked tested to prevent re-entering exhausted liquidity. |
| **Supply Zone Marking** | `test_supply_zone_marking` | RBD formation (Green rally -> Base -> Red drop) | Proximal Line = 113.0 (Lowest body of base), Distal Line = 118.0 (Highest wick of base), Zone Width = 5.0. |
| **CMP Directional Scanning** | `test_find_active_zones_relative_to_cmp` | Current Market Price CMP = 110.0 | Demand identified "Left & Down" ($PL < 110.0$); Supply identified "Left & Up" ($PL > 110.0$). Clean sorting applied. |

---

## 3. Quantitative Performance
- **Tests Run:** 4
- **Pass Rate:** 100% (4 Passed, 0 Failed, 0 Skipped)
- **Execution Latency:** 0.14 seconds
- **Linter Status:** Ruff Clean (0 errors)
