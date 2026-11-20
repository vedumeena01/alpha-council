# 🏛️ AlphaCouncil: Comprehensive Specification & Auditor Remediation (RFC v6.0)

## Problem Statement
An exhaustive institutional code audit of `alpha-council` identified critical methodological and structural issues:
1. **Synthetic Data Autocorrelation Bias:** `feed.py` generated negative lag-1 autocorrelation (-0.06 to -0.16) due to unlinked bar closes, creating an artificial mean-reversion edge for "buy the sweep".
2. **Simulation Honesty:** "Forward Paper Testing" was branded as "100% empirical proof", whereas it was executed on synthetic jump-diffusion data (seed 42).
3. **Main Backtest Low Signal Volume:** Single-stock backtest generated only 0-8 trades in 275 sessions, leaving Kelly calibration and kill switches unexercised.
4. **Unused Sentiment NLP in Backtest:** `self.nlp` and `self.triple_barrier` were instantiated in `engine.py`, but sentiment was hardcoded to `0.05`.
5. **Kill Switch Architectural Flaws:**
   - `reset_daily_session` was called once at backtest startup instead of daily, turning `intraday_hwm` into a lifetime peak.
   - `reset_monthly_session` failed to reset `intraday_hwm`, causing immediate re-halts upon monthly rollover.
   - Intraday halt was not sticky within the session.
   - `risk_committee_unfreeze` took `authorized_by` and `reason` but discarded them without an audit trail.
6. **Pre-Trade Risk Engine Early Return Bug:** Capping single-stock notional returned immediately, skipping sector cap, open risk cap, and gap-stress checks. Furthermore, `engine.py` did not supply portfolio-level metrics to `validate_order`.
7. **Optimistic Stop Fills:** Gap-down opens below stop price filled at `stop_price` rather than `min(bar.open, stop_price)`.
8. **Misleading Journal Labels:** Trailing stops exiting above entry price were labeled `STOP_LOSS_HIT` instead of `TRAILING_STOP_EXIT`.
9. **Housekeeping:** Stale test counts in README (24/24), duplicate `CONSOLIDATED_CODEBASE.md`, mismatched ATR comment in `sizing.py`, and CI missing Python 3.10 & 3.13.

## Architectural Requirements
1. **Martingale Data Generator:** Ensure $E[r_t \cdot r_{t-1}] \approx 0$ ($|\rho_1| < 0.05$).
2. **Defensive Pre-Trade Execution:** Sequential pipeline where capping feeds into subsequent sector, open risk, and gap-stress gates without early termination.
3. **Sticky & Audit-Trailed Kill Switch:** Enforce daily session resets, monthly synchronization, sticky session halts, and structured audit logs.
4. **Realistic Execution Fills:** Use `min(bar.open, stop_price)` on gap-downs with `GAP_DOWN_STOP_SLIP` classification.
5. **Accurate Journaling:** Segregate `STOP_LOSS_HIT` (loss) from `TRAILING_STOP_EXIT` (profit locked).
6. **CI & Documentation Parity:** Align CI matrix (`3.10`–`3.13`), update test badges, and clean repository duplicates.
