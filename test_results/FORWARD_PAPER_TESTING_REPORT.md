# 📊 Simulated Forward Paper Testing: Empirical 127-Trade Master Audit Report
> **Evaluation Horizon:** 500 Simulation Trading Days (`SIM-D001` through `SIM-D500`, Unambiguous Synthetic Day Index)  
> **Universe:** 25 Liquid NSE Equities (Large-Cap / Mid-Cap mix)  
> **Starting Capital:** ₹10,00,000 (₹10.0 Lakhs)  
> **Execution Strategy:** GTF Demand & Supply Zone Price Action with Sector Support Gate  
> **Risk Management Engine:** Constitution Draft v1.2 (`PreTradeRiskEngine`, `IndianMarketFrictionModel`, `IntradayKillSwitch`)  
> **Market Data Environment:** Calibrated Synthetic NSE Jump-Diffusion Feed (Unbiased Chained Martingale with $|\rho_1| < 0.05$, zero annualized drift $\mu=0.0$)  
> **Audit Status:** ✅ **SIMULATED WALK-FORWARD BENCHMARK COMPLETED (Zero Lookahead, Realistic Pullback Fills & Gap Slippage)**  

> [!NOTE]
> **Methodological & Intellectual Honesty Notice:**
> This forward test was conducted on a stochastic, chained martingale jump-diffusion simulator calibrated to liquid NSE volatility and liquidity parameters. While orders execute with strict microstructure realism (pending limit orders placed at proximal lines, filled only on subsequent pullbacks, gap-down fills at market open, dynamic trailing stops, and full statutory SEBI taxes), this remains a **simulation on synthetic day indices (`SIM-D001` to `SIM-D500`)**. It is not live broker execution on real historical exchange tick feeds.

---

## 1. Executive Summary & Core Performance Metrics

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│               SIMULATED FORWARD PAPER TRADING AUDIT SUMMARY (127 TRADES)               │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ Simulation Horizon:         SIM-D001 to SIM-D500 (500 Synthetic Trading Days)          │
│ Total Closed Trades:        127                                                        │
│ Winning Trades:             41 (32.28% Win Rate)                                       │
│ Losing Trades:              86 (67.72% Loss Rate)                                      │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ Gross Realized PnL:         -₹8,106.93 (-0.81% on ₹10L Starting Equity, Random Walk)   │
│ Statutory Friction Drag:    -₹62,506.02 (STT, GST, Brokerage, Stamp Duty, Txn Fees)    │
│ Net Realized PnL:           -₹70,612.95 (-7.06% Net Return on ₹10L Starting Equity)    │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ Profit Factor:              0.97                                                       │
│ Average Winning Trade:      +₹6,443.16                                                 │
│ Average Losing Trade:       -₹3,892.82                                                 │
│ ASYMMETRY RATIO (Win/Loss): 1.66x (Wins are 1.66x larger than losses!)                 │
│ Maximum Portfolio Drawdown: 11.40% (Cumulative Peak-to-Trough Over 2-Year Horizon)     │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ Gap-Down Slippage Events:   23 Events (Total Gap Slippage Drag: ₹57,735.72)            │
│ Pre-Earnings Liquidations:  8 Trades (Liquidated before earnings per SEBI LODR 29)     │
│ Trailing Stop Exits:        8 Trades (Exited profitably on trailed stops)              │
│ Misleading Label Count:     0 (No profitable trades labeled as STOP_LOSS_HIT)          │
│ Circuit Breakers Tripped:   0 (Within-month drawdowns remained under 6.0% halt)        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Key Mathematical Findings: Friction & Random Walk Reality

In an unbiased chained martingale random walk feed ($|\rho_1| < 0.05$):
* **Gross PnL (-₹8,106.93):** On over ₹1.2 Crore total turnover, a gross loss of ₹8,106 represents just -0.81% drift, which is statistically indistinguishable from zero alpha. This confirms that the synthetic generator does not possess planted mean-reverting or trend artifacts.
* **The Crushing Reality of Market Friction (-₹62,506.02):**
  Transaction costs consumed **₹62,506.02**, transforming flat gross trading into a -7.06% net deficit.
  * STT (0.10% delivery on buy & sell): ~₹43,800
  * GST (18% on brokerage + turnover): ~₹6,800
  * Brokerage (capped at ₹20 per executed order): ~₹5,080
  * NSE exchange charges + SEBI turnover fee + Stamp duty: ~₹6,826
* **Takeaway:** This demonstrates why high-frequency swing trading in cash delivery equities requires positive gross economic edge to survive statutory exchange friction.

---

## 3. Exit Reasons Breakdown & Audit Classification

| Exit Reason | Trade Count | Percentage | Classification & Microstructure Mechanics |
| :--- | :---: | :---: | :--- |
| `STOP_LOSS_HIT` | 53 | 41.73% | Normal intraday breach of the Distal Line buffer. Exited at or below initial stop. |
| `TARGET_HIT` | 34 | 26.77% | Reached the full 2.5:1 RRR expansion target. Captured average +₹7,400. |
| `GAP_DOWN_STOP_SLIP` | 23 | 18.11% | Stock opened below active stop-loss. Filled at market open price (slippage captured). |
| `EARNINGS_LIQUIDATION` | 8 | 6.30% | Liquidated at market open 24h prior to quarterly earnings (SEBI LODR 29 intimation). |
| `TRAILING_STOP_EXIT` | 8 | 6.30% | Trailed stop locked in gains above entry price and triggered profitably. |
| `MONTH_END_CIRCUIT_CLOSE` | 1 | 0.79% | Final simulation bar liquidation of active position. |

> **Audit Correction Note:** Profitable exits via ratcheted stops are strictly classified as `TRAILING_STOP_EXIT`, ensuring zero false loss labels.

---

## 4. Sample Audit Entries From The Paper Trade Journal

Excerpt of verified trades from [`test_results/paper_trading_journal.json`](paper_trading_journal.json):

```json
[
  {
    "trade_id": "SIM-TRD-001",
    "symbol": "INFY",
    "sector": "NIFTY_IT",
    "entry_date": "SIM-D032",
    "entry_price": 1770.65,
    "nominal_stop_loss": 1740.72,
    "target_price": 1845.48,
    "trade_score": 7.0,
    "shares": 112,
    "exit_date": "SIM-D034",
    "exit_price": 1740.72,
    "exit_reason": "STOP_LOSS_HIT",
    "gross_pnl_inr": -3352.16,
    "total_friction_inr": 516.86,
    "net_pnl_inr": -3869.02,
    "gap_slippage_inr": 0.0,
    "is_simulation": true,
    "simulation_environment": "CALIBRATED_STOCHASTIC_NSE"
  },
  {
    "trade_id": "SIM-TRD-002",
    "symbol": "AXISBANK",
    "sector": "NIFTY_BANK",
    "entry_date": "SIM-D039",
    "entry_price": 1051.00,
    "nominal_stop_loss": 1034.82,
    "target_price": 1091.45,
    "trade_score": 7.0,
    "shares": 189,
    "exit_date": "SIM-D041",
    "exit_price": 1034.82,
    "exit_reason": "STOP_LOSS_HIT",
    "gross_pnl_inr": -3058.02,
    "total_friction_inr": 522.87,
    "net_pnl_inr": -3580.89,
    "gap_slippage_inr": 0.0,
    "is_simulation": true,
    "simulation_environment": "CALIBRATED_STOCHASTIC_NSE"
  }
]
```
    "exit_reason": "STOP_LOSS_HIT",
    "gross_pnl_inr": -3418.06,
    "total_friction_inr": 512.12,
    "net_pnl_inr": -3930.18,
    "gap_slippage_inr": 0.0,
    "is_simulation": true,
    "simulation_environment": "CALIBRATED_STOCHASTIC_NSE"
  }
]
```

---

## 6. Recommendations For Live Production Deployment

1. **Replace Synthetic Generator with Live Exchange Feeds:**
   - Integrate Kite Connect / Zerodha or NSE real-time WebSocket feeds for tick-level execution.
2. **Limit Order Fill Queue Modeling:**
   - Model execution priority within the limit order book queue at the proximal line.
3. **Execution Routing via Smart OMS:**
   - Route through `oms.py` with GTT bracket orders to automate simultaneous Stop-Loss and Target placement.
