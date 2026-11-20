# 🗺️ AlphaCouncil: Remediation Roadmap (Round 2)

## Milestones & Tasks

- [ ] **Task 1: Trade Frequency & Kelly/BSS Path Calibration**
  - [ ] In `alphacouncil/config.py`: Reduce `cold_start_trade_threshold` from rigid 200 to 50 so that realistic swing trading portfolios can exercise Kelly/BSS calibration within 250–500 bars.
  - [ ] In `alphacouncil/backtest/ablation.py`: Ensure `run_full_suite()` runs across multi-symbol universe (or 5–10 symbols) rather than 1 stock, generating 50+ trades.
  - [ ] Add unit test in `tests/test_risk_engine.py` verifying the transition from COLD_START to calibrated KELLY/DEFENSIVE sizing when closed trades exceed the threshold.

- [ ] **Task 2: PITCH_DECK.md Slide 5 Overhaul & Removal of "Proof"**
  - [ ] Rebrand Slide 5 to "Architectural Ablation: Isolating Alpha & Risk Mechanics".
  - [ ] Replace single-seed cherry-picked Sharpe 2.40 / PF 5.20 with honest multi-seed aggregated metrics and explicit variance caveats.
  - [ ] State clearly that data is synthetic jump-diffusion simulation, not historical exchange tick data.
  - [ ] Remove all instances of the word "Proof" across `PITCH_DECK.md`, `FORWARD_PAPER_TESTING_REPORT.md`, and `README.md`.

- [ ] **Task 3: Transparent Sentiment Featurizer Labeling**
  - [ ] In `alphacouncil/alpha/sentiment_nlp.py` and `alphacouncil/data/calendar.py`: Label `FinBertSentimentExtractor` and `get_latest_headline` explicitly as a research prototype stub / synthetic structural lexicon test fixture.
  - [ ] State clearly in docs and code docstrings that in live production this module connects to real-time SEBI corporate filings / RSS feeds.

- [ ] **Task 4: Simulation Dates Realism & Marking**
  - [ ] In `alphacouncil/data/feed.py`: Anchor simulation starting date to `2023-01-01` so that 500 daily sessions span strictly past historical dates (`2023-01-01` to `2024-12-05`), never bleeding into late 2026.
  - [ ] In `PaperTradeRecord`: Add `"is_simulation": True` and `"environment": "SIMULATED_STOCHASTIC_NSE"`.
  - [ ] Re-run paper simulation to refresh `paper_trading_journal.json`.

- [ ] **Task 5: Re-Verification & CI Pipeline**
  - [ ] Run full test suite (`pytest -v`), check linter (`ruff check .`).
  - [ ] Update `CONSOLIDATED_CODEBASE.md`.
  - [ ] Repack Desktop backup zip.
  - [ ] Commit, push to `origin/main`, and verify GitHub Actions CI run.
