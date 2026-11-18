# 📊 Test Results: Episode 2
> **Episode Title:** Why Does Stock Price Go Up and Down? (Demand/Supply & 50% Body Rule)  
> **Source Module:** `alphacouncil/alpha/zone_engine.py`  
> **Test File:** `tests/test_zone_engine.py`  
> **Status:** ✅ **100% PASSED**  
> **Execution Timestamp:** 2026-11-18 17:10 IST

---

## 1. Test Command & Execution Output
```bash
pytest -v tests/test_zone_engine.py -k "classification"
```

```text
============================= test session starts =============================
platform win32 -- Python 3.13.13, pytest-9.1.1, pluggy-1.7.0 -- C:\Python313\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\vedpr\OneDrive\Desktop\alpha-council
configfile: pyproject.toml
plugins: anyio-4.14.2, platformdirs-4.13.5, cov-7.1.0
collecting ... collected 13 items / 12 deselected / 1 selected

tests/test_zone_engine.py::test_candle_classification_exciting_vs_base PASSED [100%]

====================== 1 passed, 12 deselected in 0.15s =======================
```

---

## 2. Capabilities Tested & Verified

| Feature / Concept | Test Function | Input / Scenario | Assertion & Outcome |
| :--- | :--- | :--- | :--- |
| **Green Exciting Candle** | `test_candle_classification_exciting_vs_base` | Open 100, High 112, Low 99, Close 110 (Body 10 / Range 13 = 76.9%) | Classified as `GREEN_EXCITING` ($\text{Body Ratio} \ge 0.50$). Confirms buyers overwhelmed sellers. |
| **Red Exciting Candle** | `test_candle_classification_exciting_vs_base` | Open 110, High 111, Low 98, Close 100 (Body 10 / Range 13 = 76.9%) | Classified as `RED_EXCITING` ($\text{Body Ratio} \ge 0.50$). Confirms aggressive institutional selling. |
| **Base Candle (Basing)** | `test_candle_classification_exciting_vs_base` | Open 105, High 115, Low 95, Close 106 (Body 1 / Range 20 = 5.0%) | Classified as `BASE` ($\text{Body Ratio} < 0.50$). Equilibrium tug-of-war where pending orders accumulate. |

---

## 3. Quantitative Performance
- **Tests Run:** 1 (Multi-scenario assertion)
- **Pass Rate:** 100% (1 Passed, 0 Failed, 0 Skipped)
- **Execution Latency:** 0.15 seconds
- **Linter Status:** Ruff Clean (0 errors)
