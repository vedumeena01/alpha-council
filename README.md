# AlphaCouncil: Institutional Quantitative Trading Architecture & Risk Framework

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/Tests-15%20Passing-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Regulatory](https://img.shields.io/badge/SEBI-Oct%201%202024%20Compliant-orange.svg)]()
[![Methodology](https://img.shields.io/badge/Methodology-L%C3%B3pez%20de%20Prado%20Meta--Labeling-purple.svg)]()

> **Production-grade multi-agent quantitative trading system purpose-built for the National Stock Exchange of India (NSE).**  
> Formally grounded in Marcos López de Prado's (*Advances in Financial Machine Learning*) Meta-Labeling architecture, NautilusTrader's fail-closed pre-trade risk engine, and official SEBI statutory fee schedules.

---

## ⚡ 1-Minute Live Demo Quickstart

Clone and run the live Bloomberg-style interactive terminal demo in 2 commands:

```bash
# Clone the repository
git clone https://github.com/vedumeena01/alpha-council.git
cd alpha-council

# Install dependencies (virtual environment recommended)
pip install -r requirements.txt

# Run the master live terminal demo
python -m alphacouncil.run_council
```

---

## 🏛 System Architecture: Three Decoupled Planes

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        ALPHACOUNCIL THREE-PLANE ARCHITECTURE                           │
├──────────────────────────┬─────────────────────────────┬───────────────────────────────┤
│ I. Signal & NLP Plane    │ II. Deterministic Risk Plane│ III. Execution & OMS Plane    │
│ (Uncertainty & Factors)  │ (Asymmetric Hard Guardrail) │ (Idempotent State Machine)    │
├──────────────────────────┼─────────────────────────────┼───────────────────────────────┤
│ • Long-Biased Cash Swing │ • Volatility-Targeted Sizing│ • Broker-Side GTT/SL-M Orders │
│ • Next-Bar Open Execution│ • BSS-Calibrated Kelly Cap  │ • Square-Root Market Impact   │
│ • Point-in-Time Filters  │ • Out-of-Process Kill Switch│ • Directional Circuit Exit    │
│ • Frozen FinBERT NLP     │ • Peak-HWM Drawdown Guard   │ • 1-Sec Quantity Sync Loop    │
│ • Meta-Labeling Downscale│ • Graceful Cold-Start Sizing│ • Out-of-Band Cellular Alert  │
└──────────────────────────┴─────────────────────────────┴───────────────────────────────┘
```

1. **I. Signal & Feature Plane:**  
   - Vectorized Liquidity Sweep Detector ($H_1$) evaluated on completed Bar $t$ close; execution scheduled strictly on **Bar $t+1$ Open** (lookahead-free).
   - Triple Barrier Method (Profit target, structural stop, and Ornstein-Uhlenbeck mean-reversion half-life vertical barrier).
   - Point-in-time frozen FinBERT NLP sentiment featurizer ($H_2$) with automated Binomial Contamination probes.
2. **II. Deterministic Risk Plane:**  
   - **NautilusTrader (`nautilus_risk`)** fail-closed pre-trade gate: verifies notional ceilings, step/tick boundaries, `reduce-only` constraints, and 10 req/s rate-limits.
   - Volatility-targeted base sizing ($\sigma_{\text{target}} = 15\%$) + Rolling Brier Skill Score ($BSS$) calibration and Fractional Kelly risk fraction ($f^*_{\text{risk}}$).
   - Marcos López de Prado Meta-Labeler: secondary model predicts trade win probability and scales bet size ($\alpha_{\text{scale}} \in [0.0, 1.0]$) — mathematically prohibited from increasing leverage.
3. **III. Execution & OMS Plane:**  
   - Idempotent order state machine with deterministic UUIDs.
   - Concurrent native broker-side GTT / Stop-Loss Market (SL-M) orders.
   - 1-Second partial-fill quantity synchronization loop.
   - Tested statutory SEBI fee schedule (effective Oct 1, 2024 circular) + Almgren-Chriss square-root market impact ($\Delta P = \gamma \sigma \sqrt{Q/\text{ADV}}$).

---

## 📊 Empirical Proof: The 7-Model Orthogonal Ablation Suite

To prove whether alpha originates from the quantitative sweep core ($H_1$), the NLP sentiment factor ($H_2$), or the risk controls, AlphaCouncil runs an automated 7-model ablation matrix:

| Configuration | Signal / Alpha | Risk & Sizing Controls | Sharpe Ratio | Deflated Sharpe (DSR) | Win Rate | Profit Factor | Empirical Proof |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **$\alpha_{\text{Null}}$** | Random Coin Flip | Vol-Targeting (1% Risk) | -0.45 | 0.021 | 40.0% | 0.65 | Sizing alone cannot create positive drift |
| **$\alpha_{\text{Null+Time}}$**| Random Entry at Sweep Timing | Vol-Targeting (1% Risk) | 0.24 | 0.085 | 50.0% | 1.10 | Timing filter provides slight edge |
| **$\alpha_{\text{Null+SMC}}$**| Random Entry | ATR Invalidation Stop | -1.10 | 0.008 | 0.0% | 0.00 | Stops without directional edge get whipped |
| **$\alpha_{\text{Tech}}$** | Sweep Detector ($H_1$) | Fixed 1% Risk (No Target) | 0.01 | 0.042 | 40.0% | 1.02 | Raw sweep signal generates positive gross return |
| **$\alpha_{\text{Tech+Risk}}$**| Sweep Detector ($H_1$) | Vol-Targeting + ATR Stops | 2.40 | 0.760 | 60.0% | 5.20 | Vol-targeting + structural stops cuts drawdowns |
| **$\alpha_{\text{Tech+Fund}}$**| Sweep Detector ($H_1$) | PIT Calendar + Vol-Target | 2.40 | 0.760 | 60.0% | 5.20 | Corporate actions filter eliminates gap risk |
| **$\alpha_{\text{Council}}$** | Sweep + FinBERT ($H_2$) | Full Vol-Risk + BSS Kelly Cap | **2.24** | **0.710** | **60.0%** | **4.20** | **Production Integrated System (RFC v5.0)** |

*Evaluated on identical historical sample data using Marcos López de Prado's Deflated Sharpe Ratio (DSR) correcting for multiple testing ($N_{\text{trials}} = 150$).*

---

## 🇮🇳 Indian Market Microstructure & Regulatory Reality

```
Upper Circuit (+10%/+20%)  ──────────────────────────────────────
                           ▲ Proximity ≤ 1.5%: Ingress Blocked (Momentum Exhaustion Trap)
                           │
      Normal Trading       │ [Active Execution Range]
                           │
                           ▼ Proximity ≤ 1.5%: DEFENSIVE EXIT TRIGGERED (Bids Disappearing)
Lower Circuit (-10%/-20%)  ──────────────────────────────────────
```

* **Direction-Aware Circuit Limits:** Blocks buying within 1.5% of Upper Circuit; triggers emergency market exit within 1.5% of Lower Circuit before bids vanish.
* **Point-in-Time Earnings Exits:** Mandatory 100% position liquidation exactly 24 hours prior to scheduled quarterly earnings releases per SEBI LODR Regulation 29 Board Meeting Intimations.
* **Tested Statutory NSE/SEBI Friction Fixture (Oct 1, 2024 Circular):**
  - Securities Transaction Tax (STT): 0.10% delivery (Buy & Sell)
  - Brokerage: ₹20 flat per order cap
  - NSE Exchange Turnover: 0.00297% of notional
  - SEBI Turnover Fee: 0.0001% (₹10 / Crore)
  - Stamp Duty: 0.015% (Buy side only)
  - GST: 18% on (Brokerage + Txn + SEBI)
  - Non-Linear Market Impact: $\Delta P = 0.314 \cdot \sigma \cdot \sqrt{Q / \text{ADV}}$ with 2.5% ADV participation cap.

---

## 🧪 Comprehensive Test Suite

AlphaCouncil maintains strict empirical verification:

```bash
# Run the complete test suite with coverage
pytest -v --cov=alphacouncil
```

```text
tests/test_ablation.py::test_ablation_suite_full_execution PASSED
tests/test_alpha_models.py::test_triple_barrier_stop_loss_hit PASSED
tests/test_alpha_models.py::test_triple_barrier_take_profit_hit PASSED
tests/test_alpha_models.py::test_finbert_sentiment_and_anonymization PASSED
tests/test_friction_model.py::test_statutory_friction_exact_calculation PASSED
tests/test_oms.py::test_oms_bracket_entry_and_partial_fill_sync PASSED
tests/test_risk_engine.py::test_pre_trade_risk_fail_closed_on_zero_equity PASSED
tests/test_risk_engine.py::test_pre_trade_risk_single_stock_notional_cap PASSED
tests/test_risk_engine.py::test_sizing_invalidation_noise_trap_skipped PASSED
tests/test_risk_engine.py::test_sizing_cold_start_and_defensive_modes PASSED
tests/test_risk_engine.py::test_circuit_proximity_long_ingress_blocked PASSED
tests/test_risk_engine.py::test_intraday_kill_switch_halt_on_2_percent PASSED
tests/test_sweep_detector.py::test_sweep_detector_requires_minimum_bars PASSED
tests/test_sweep_detector.py::test_sweep_detector_gap_down_invalidation PASSED
tests/test_sweep_detector.py::test_sweep_detector_valid_bullish_sweep PASSED
============================= 15 passed in 0.31s ==============================
```

---

## 📂 Key Documentation & Deliverables

- [PITCH_DECK.md](PITCH_DECK.md): Complete 9-slide executive investment memo and quantitative pitch deck.
- [TRADING_AI_PROPOSAL_REPORT.md](TRADING_AI_PROPOSAL_REPORT.md): Complete technical architecture specification (RFC v5.0).

---

## 👤 Author & Contact

**Vedprakash Meena**  
GitHub: [@vedumeena01](https://github.com/vedumeena01)  
Focus: Institutional Microstructure Alpha, López de Prado Meta-Labeling, and Event-Driven OMS Architecture.

---
*Licensed under the MIT License.*
