# 📊 Test Results: Episode 4
> **Episode Title:** Best Way to Mark Entry, Stoploss and Target (Exceptional Marking & 2:1 RRR)  
> **Source Module:** `alphacouncil/alpha/zone_engine.py`  
> **Test File:** `tests/test_zone_engine.py`  
> **Status:** ✅ **100% PASSED**  
> **Execution Timestamp:** 2026-11-18 17:10 IST

---

## 1. Test Command & Execution Output
```bash
pytest -v tests/test_zone_engine.py -k "exceptional or execution_orders"
```

```text
============================= test session starts =============================
platform win32 -- Python 3.13.13, pytest-9.1.1, pluggy-1.7.0 -- C:\Python313\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\vedpr\OneDrive\Desktop\alpha-council
configfile: pyproject.toml
plugins: anyio-4.14.2, platformdirs-4.13.5, cov-7.1.0
collecting ... collected 13 items / 7 deselected / 6 selected

tests/test_zone_engine.py::test_exceptional_marking_dbr_vedanta_case_study PASSED [ 16%]
tests/test_zone_engine.py::test_exceptional_marking_dbr_alkyl_amines_case_study PASSED [ 33%]
tests/test_zone_engine.py::test_exceptional_marking_rbr_continuous_strictly_ignores_leg_in PASSED [ 50%]
tests/test_zone_engine.py::test_exceptional_marking_continuous_rbr_with_leg_out_wick PASSED [ 66%]
tests/test_zone_engine.py::test_exceptional_marking_supply_patterns PASSED [ 83%]
tests/test_zone_engine.py::test_execution_orders_entry_sl_target_calculations PASSED [100%]

======================= 6 passed, 7 deselected in 0.14s =======================
```

---

## 2. Capabilities Tested & Verified

| Feature / Concept | Test Function | Input / Scenario | Assertion & Outcome |
| :--- | :--- | :--- | :--- |
| **Vedanta DBR Exception** | `test_exceptional_marking_dbr_vedanta_case_study` | Leg-in lower wick extends to 190.0, Base low at 198.0 | Proximal Line stays invariant at 203.0. Normal DL = 198.0; Exceptional DL = 190.0. Absorbs deep retest spikes. |
| **Alkyl Amines Dual Wick** | `test_exceptional_marking_dbr_alkyl_amines_case_study` | Both Leg-in (255.0) and Leg-out (250.0) dip below Base (258.0) | Exceptional DL takes the absolute lowest wick = 250.0 (Leg-out wick). |
| **Continuous RBR Leg-in Isolation** | `test_exceptional_marking_rbr_continuous_strictly_ignores_leg_in` | RBR continuous setup where Leg-in has historical wick down to 85.0 | Leg-in wick strictly ignored. Exceptional DL = 125.0 (Base low), not 85.0. |
| **Continuous RBR Leg-out Wick** | `test_exceptional_marking_continuous_rbr_with_leg_out_wick` | Leg-out dips to 122.0 before rallying, Base low at 125.0 | DL successfully shifts to Leg-out wick = 122.0. |
| **Supply Reversal & Continuous** | `test_exceptional_marking_supply_patterns` | RBD (Reversal) evaluates Leg-in peak (155.0); DBD (Continuous) ignores Leg-in peak (200.0) | RBD DL = 155.0; DBD DL = 148.0 (evaluates only Base & Leg-out). |
| **Execution Order Levels** | `test_execution_orders_entry_sl_target_calculations` | Demand setup: PL 200.0, DL 190.0, 5% buffer | Entry = 200.50 (above PL), SL = 189.50 (below DL buffer), Target = 222.50 (exact 2:1 RRR). |

---

## 3. Quantitative Performance
- **Tests Run:** 6
- **Pass Rate:** 100% (6 Passed, 0 Failed, 0 Skipped)
- **Execution Latency:** 0.14 seconds
- **Linter Status:** Ruff Clean (0 errors)
