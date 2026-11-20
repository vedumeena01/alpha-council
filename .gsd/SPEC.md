# 🏛️ AlphaCouncil: Comprehensive Specification & Auditor Remediation (RFC v6.0)

## Problem Statement (Auditor Review Round 2)
An exhaustive review identified remaining issues:
1. **Low Trade Frequency in Ablation/Backtest:** Single-stock sweep signals produce only 3–6 trades in 275 sessions, leaving the 200-trade Kelly/BSS calibration path unexercised across seeds.
2. **`PITCH_DECK.md` Slide 5 Numbers:** The Sharpe 2.40 / PF 5.20 claims do not reproduce across seeds due to 3–6 trade sample noise, and claim "verified on historical sample data" when data is synthetic.
3. **Sentiment Signal Realism:** `get_latest_headline` produces synthetic canned strings from hash(symbol+date); it must be explicitly labeled as a synthetic lexicon prototype stub.
4. **Journal Dates Misleading:** Dates ending in 2026-11-24 resemble future live dates; must be anchored to historical dates or explicitly prefixed with `SIM-`.
5. **Overclaiming "Proof":** The word "Proof" is still present in report titles and pitch deck; must be eliminated in favor of "Simulation Benchmark" and "Verification".

## Architectural Requirements
1. **Multi-Stock / Calibrated Trade Generation:** Support multi-symbol evaluation in `ablation.py` and adjust lookback/thresholds so sufficient trades (50-100+) occur to test Kelly transitions.
2. **Honest Pitch Deck:** Update Slide 5 with realistic multi-seed architectural comparison and explicit caveats about sample size and synthetic data.
3. **Transparent Sentiment Featurizer:** Label FinBERT in simulation as a research stub / synthetic test fixture.
4. **Unambiguous Simulation Dates:** Anchor synthetic simulation dates to historical past (e.g. 2023–2024) and mark records with `is_simulation: True`.
5. **Zero "Proof" Wording:** Rebrand all files and headings to eliminate the word "Proof".
