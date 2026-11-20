# 🗺️ AlphaCouncil: Remediation Roadmap

## Milestones & Tasks

- [ ] **Phase 1: Pre-Trade Risk Engine & Kill Switch Core Bug Fixes**
  - [ ] Fix `alphacouncil/risk/pre_trade.py`: Remove early return on 20% notional capping; ensure downstream checks (sector cap, 3% open risk, 2x gap stress) run on `adjusted_quantity`.
  - [ ] Fix `alphacouncil/risk/kill_switch.py`:
    - Add structured audit log to `risk_committee_unfreeze` recording timestamp, authorized_by, reason, and prior state.
    - Synchronize `reset_monthly_session` to reset both `monthly_hwm` and `intraday_hwm`.
    - Make intraday session halt sticky until explicit `reset_daily_session` call.
  - [ ] Add unit tests in `tests/test_risk_engine.py` covering:
    - Capped quantity flowing into sector and open risk checks.
    - Sticky session halt.
    - Audit-trailed unfreeze logging.
    - Monthly rollover without false re-halt.

- [ ] **Phase 2: Execution & Backtest Realism Fixes**
  - [ ] Fix `alphacouncil/backtest/engine.py`:
    - Fix stop fills to `min(bar.open, pos["stop_price"])` and classify gap slips.
    - Call `self.kill_switch.reset_daily_session()` on each daily bar.
    - Pass open risk, sector notional, and stop loss to `self.pre_trade.validate_order()`.
    - Utilize `self.nlp.extract_sentiment()` on news/announcements and integrate `TripleBarrierLabeler`.
  - [ ] Fix `alphacouncil/execution/paper_trader.py`:
    - Classify stops triggered with `exit_price > entry_price` as `ExitReason.TRAILING_STOP_EXIT` instead of `ExitReason.STOP_LOSS_HIT`.
    - Re-run paper simulation and update `test_results/paper_trading_journal.json` and `test_results/FORWARD_PAPER_TESTING_REPORT.md`.

- [ ] **Phase 3: Synthetic Data Generator Unbiased Martingale Calibration**
  - [ ] Redesign `MarketDataFeed.generate_series` in `alphacouncil/data/feed.py` so price bars sequentially link `close[t-1] -> open[t] -> close[t]`.
  - [ ] Verify across multiple seeds that lag-1 return autocorrelation is close to 0 ($|\rho_1| < 0.05$).
  - [ ] Verify all existing tests pass under the corrected price generator.

- [ ] **Phase 4: Documentation, Claims Honesty & Housekeeping**
  - [ ] Clarify simulated nature in `test_results/FORWARD_PAPER_TESTING_REPORT.md` (no false claims of live market proof).
  - [ ] Fix stale comment in `alphacouncil/risk/sizing.py` (`1.0*ATR` -> `0.25*ATR`).
  - [ ] Update `README.md` and `CODE_REVIEW_REPORT.md` with accurate test counts (126+ tests).
  - [ ] Update `.github/workflows/ci.yml` matrix to `["3.10", "3.11", "3.12", "3.13"]`.
  - [ ] Clean duplicate `docs/CONSOLIDATED_CODEBASE.md` into a pointer and regenerate consolidated codebase.
  - [ ] Repack Desktop backup zip.
