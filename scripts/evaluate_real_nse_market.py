"""
Real NSE Market Data Empirical Evaluation & Stabilization Harness.
Runs GTF Zone Engine, Sweep Detector, and the full 7-Model Orthogonal
Ablation Suite across 10 liquid NSE equities on real 2-year market history.
"""

import os
import json
import numpy as np
from typing import Dict, List

from alphacouncil.data.feed import Bar
from alphacouncil.backtest.ablation import AblationSuiteRunner
from alphacouncil.alpha.sweep_detector import LiquiditySweepDetector
from alphacouncil.alpha.zone_engine import DemandSupplyEngine
from alphacouncil.config import AlphaCouncilConfig, StatutoryFeeConfig

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(REPO_ROOT, "alphacouncil", "data", "real_cache")
REAL_SYMBOLS = [
    "RELIANCE",
    "INFY",
    "TCS",
    "HDFCBANK",
    "ICICIBANK",
    "SBIN",
    "BHARTIARTL",
    "LT",
    "ITC",
    "AXISBANK",
]


def load_real_data() -> Dict[str, List[Bar]]:
    data: Dict[str, List[Bar]] = {}
    for sym in REAL_SYMBOLS:
        p = os.path.join(CACHE_DIR, f"{sym}_2y.json")
        if not os.path.exists(p):
            continue
        with open(p) as f:
            items = json.load(f)
        data[sym] = [Bar(**it) for it in items]
    return data


def run_gtf_price_action_audit(data: Dict[str, List[Bar]]):
    print("=" * 100)
    print("1. GTF PRICE ACTION & ZONE ENGINE REAL-MARKET AUDIT (10 Liquid NSE Stocks, 2 Years Daily)")
    print("=" * 100)
    zone_engine = DemandSupplyEngine()
    sweep_detector = LiquiditySweepDetector(lookback=15, volume_factor=1.1)

    total_exciting = 0
    total_base = 0
    total_demand_zones = 0
    total_supply_zones = 0
    total_fresh_demand = 0
    total_sweeps = 0

    print(f"{'Symbol':11} | {'Bars':5} | {'Exciting':8} | {'Base':6} | {'Demand':7} | {'Fresh Dem':9} | {'Supply':7} | {'Sweeps':6} | {'Latest Zone Setup':30}")
    print("-" * 100)

    for sym, bars in data.items():
        opens = np.array([b.open for b in bars], dtype=float)
        highs = np.array([b.high for b in bars], dtype=float)
        lows = np.array([b.low for b in bars], dtype=float)
        closes = np.array([b.close for b in bars], dtype=float)
        atrs = np.array([b.atr14 for b in bars], dtype=float)

        volumes = np.array([b.volume for b in bars], dtype=float)

        # Candle classification
        n_exc = 0
        n_bas = 0
        for b in bars:
            rng = b.high - b.low
            body = abs(b.close - b.open)
            if rng > 0 and (body / rng) > 0.50:
                n_exc += 1
            else:
                n_bas += 1
        total_exciting += n_exc
        total_base += n_bas

        # Scan for GTF zones
        zones = zone_engine.scan_for_zones(opens, highs, lows, closes, atr14=atrs)
        d_zones = [z for z in zones if z.is_demand]
        s_zones = [z for z in zones if not z.is_demand]
        fresh_d = [z for z in d_zones if z.is_fresh]

        total_demand_zones += len(d_zones)
        total_supply_zones += len(s_zones)
        total_fresh_demand += len(fresh_d)

        # Detect sweeps using scan_series
        sweep_signals = sweep_detector.scan_series(sym, opens, highs, lows, closes, volumes)
        sweeps = len(sweep_signals)
        total_sweeps += sweeps

        latest_info = "No fresh zones"
        if fresh_d:
            lz = fresh_d[-1]
            latest_info = f"PL: ₹{lz.proximal_line:,.1f} | DL: ₹{lz.distal_line:,.1f} | Score {lz.trade_score}/7"

        print(f"{sym:11} | {len(bars):5} | {n_exc:8} | {n_bas:6} | {len(d_zones):7} | {len(fresh_d):9} | {len(s_zones):7} | {sweeps:6} | {latest_info:30}")

    print("-" * 100)
    total_bars = sum(len(b) for b in data.values())
    print(f"{'TOTAL':11} | {total_bars:5} | {total_exciting:8} | {total_base:6} | {total_demand_zones:7} | {total_fresh_demand:9} | {total_supply_zones:7} | {total_sweeps:6}")
    print(f"Empirical Exciting Candle Ratio: {total_exciting / (total_exciting + total_base) * 100:.1f}%")
    print(f"Empirical Base Candle Ratio:     {total_base / (total_exciting + total_base) * 100:.1f}%\n")


def run_ablation_on_real_data(data: Dict[str, List[Bar]]):
    print("=" * 100)
    print("2. 7-MODEL ORTHOGONAL ABLATION SUITE ON REAL NSE MARKET DATA (496 BARS / 2 YEARS)")
    print("=" * 100)

    # 1. Full Statutory Friction Run
    runner_fric = AblationSuiteRunner(n_trials_logged=150, seed=42, tie_break="stop_first")
    results_fric = runner_fric.run_full_suite(data)

    print("\n--- A. Real NSE Equities (FULL STATUTORY SEBI FRICTION SCHEDULE) ---")
    print(f"{'Configuration':22} | {'Trades':6} | {'Sharpe':7} | {'DSR':7} | {'Gross PnL':12} | {'Friction':10} | {'Net PnL':12} | {'Win Rate':8}")
    print("-" * 95)
    for k, res in results_fric.items():
        m = res.metrics
        n_trades = len(res.trades)
        gross = float(sum(t.gross_pnl_inr for t in res.trades))
        fric = float(sum(t.friction_inr for t in res.trades))
        net = float(sum(t.net_pnl_inr for t in res.trades))
        wr = f"{m.win_rate_pct:.1f}%"
        print(f"{k:22} | {n_trades:6} | {m.sharpe_ratio:7.2f} | {m.deflated_sharpe_ratio:7.4f} | ₹{gross:11,.0f} | ₹{fric:9,.0f} | ₹{net:11,.0f} | {wr:8}")

    # 2. Zero Friction Run (Isolating Pure Alpha on Real Data)
    zero_fees = StatutoryFeeConfig(
        stt_delivery_rate=0.0,
        stt_intraday_sell_rate=0.0,
        brokerage_per_order_cap=0.0,
        brokerage_rate=0.0,
        exchange_txn_charge_rate=0.0,
        sebi_turnover_rate=0.0,
        stamp_duty_buy_rate=0.0,
        gst_rate=0.0,
        market_impact_gamma=0.0,
    )
    cfg_zero = AlphaCouncilConfig(fees=zero_fees)
    runner_zero = AblationSuiteRunner(n_trials_logged=150, seed=42, config=cfg_zero, tie_break="stop_first")
    results_zero = runner_zero.run_full_suite(data)

    print("\n--- B. Real NSE Equities (ZERO FRICTION BENCHMARK — PURE REAL-MARKET ALPHA) ---")
    print(f"{'Configuration':22} | {'Trades':6} | {'Sharpe':7} | {'DSR':7} | {'Gross PnL':12} | {'Win Rate':8} | {'Profit Factor':13}")
    print("-" * 90)
    for k, res in results_zero.items():
        m = res.metrics
        n_trades = len(res.trades)
        gross = float(sum(t.gross_pnl_inr for t in res.trades))
        wr = f"{m.win_rate_pct:.1f}%"
        pf = f"{m.profit_factor:.2f}"
        print(f"{k:22} | {n_trades:6} | {m.sharpe_ratio:7.2f} | {m.deflated_sharpe_ratio:7.4f} | ₹{gross:11,.0f} | {wr:8} | {pf:13}")


if __name__ == "__main__":
    real_data = load_real_data()
    print(f"Loaded real market history for {len(real_data)} symbols.")
    run_gtf_price_action_audit(real_data)
    run_ablation_on_real_data(real_data)
