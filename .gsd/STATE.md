# 🧠 AlphaCouncil: Session Memory & State

## Current Context
- **Active Phase:** Round 4 Institutional Auditor Remediation Complete & Verified
- **Branch:** `main`
- **Current Test Suite Status:** 131/131 passed in 7.94s
- **Linter Status:** Ruff 0 errors, 0 warnings
- **CI Matrix:** Python 3.10, 3.11, 3.12, 3.13

## Verification & Remediation Log (Round 4 Auditor Review)
1. **Slide 5 Ablation Table Exact Reproduction:**
   - Synchronized `PITCH_DECK.md` Slide 5 with exact outputs of `generate_ablation_distribution.py` run on the current `SIM-D` codebase.
   - Displayed both universes side-by-side: 5 symbols (30 seeds, 250 bars) and 25 symbols (30 seeds, 500 bars).
   - Removed all unearned claims like "risk truncation works". Transparently documented that every configuration generates negative median Sharpe under statutory Indian friction on zero-alpha feeds, and that DSR is appropriately ~0.0010.
2. **Exported Constants in Code:**
   - Defined and exported `PROD_THRESHOLD = 200`, `PROD_KELLY_THRESHOLD = 200`, and `HARNESS_KELLY_THRESHOLD = 50` directly in `alphacouncil/config.py` and `alphacouncil/risk/sizing.py`.
3. **Deterministic Hashing:**
   - Replaced all non-cryptographic hashes in `calendar.py` and `sentiment_nlp.py` with `hashlib.sha256`, guaranteeing 100% independence from `PYTHONHASHSEED`.
4. **Description Alignment:**
   - Standardized `alpha_Null_Time` description to `"Random Entry + PIT Filter"` across scripts and deck.
5. **Release Zip Cleanliness:**
   - Repacked 100 clean files into `alpha_council_complete_codebase.zip` (445.0 KB) with 0 forbidden files.
