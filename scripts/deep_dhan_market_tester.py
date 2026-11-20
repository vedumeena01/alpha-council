"""
Deep Market & DhanHQ API Integration Test Harness.
Executes an end-to-end walk-forward session simulation across 10 liquid NSE equities (4,960 bars)
routing real GTF Demand Zone & Sweep signals directly through the DhanExecutionAdapter.
Captures all failures, exceptions, tick-size errors, and edge-case rejections.
"""

import os
import json
import numpy as np
from typing import Dict, List, Any

from alphacouncil.data.feed import Bar
from alphacouncil.execution.dhan_adapter import DhanExecutionAdapter, DhanProductType
from alphacouncil.alpha.sweep_detector import LiquiditySweepDetector

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


def run_deep_dhan_simulation(data: Dict[str, List[Bar]], initial_capital: float = 1_000_000.0) -> Dict[str, Any]:
    adapter = DhanExecutionAdapter(sandbox_mode=True)
    sweep_detector = LiquiditySweepDetector(lookback=15, volume_factor=1.1)

    total_bars_evaluated = 0
    signals_detected = 0
    orders_attempted = 0
    orders_succeeded = 0
    orders_rejected = 0
    exceptions_encountered = []
    rejection_reasons = {}

    r_per_trade = initial_capital * 0.01  # 1% risk = ₹10,000

    print(f"Starting Deep Walk-Forward DhanHQ Simulation across {len(data)} symbols...")

    for sym, bars in data.items():
        n_bars = len(bars)
        total_bars_evaluated += n_bars

        opens = np.array([b.open for b in bars], dtype=float)
        highs = np.array([b.high for b in bars], dtype=float)
        lows = np.array([b.low for b in bars], dtype=float)
        closes = np.array([b.close for b in bars], dtype=float)
        volumes = np.array([b.volume for b in bars], dtype=float)

        # Walk forward through bars
        for i in range(30, n_bars - 1):
            curr_bar = bars[i]

            # 1. Sweep signal evaluation matching scan_series slicing
            sig = sweep_detector.evaluate_bar(
                symbol=sym,
                open_p=opens[: i + 1],
                high=highs[: i + 1],
                low=lows[: i + 1],
                close=closes[: i + 1],
                volume=volumes[: i + 1],
                bar_idx=i,
            )
            if not sig or sig.signal != 1:
                continue

            signals_detected += 1
            entry_price = round(curr_bar.close, 2)
            stop_loss = round(sig.structural_stop, 2)
            target_price = round(entry_price + 2.0 * (entry_price - stop_loss), 2)

            risk_per_share = entry_price - stop_loss
            if risk_per_share <= 0:
                continue

            quantity = int(r_per_trade / risk_per_share)
            orders_attempted += 1

            try:
                res = adapter.place_gtt_oco_bracket(
                    symbol=sym,
                    quantity=quantity,
                    entry_price=entry_price,
                    target_price=target_price,
                    stop_loss_price=stop_loss,
                    product_type=DhanProductType.CNC,
                )
                if res.success:
                    orders_succeeded += 1
                else:
                    orders_rejected += 1
                    reason = res.message or "UNKNOWN_REJECTION"
                    rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1
            except Exception as e:
                orders_rejected += 1
                exc_str = f"{type(e).__name__}: {str(e)}"
                exceptions_encountered.append({
                    "symbol": sym,
                    "bar_date": curr_bar.timestamp,
                    "entry": entry_price,
                    "target": target_price,
                    "stop": stop_loss,
                    "qty": quantity,
                    "exception": exc_str,
                })
                rejection_reasons[exc_str] = rejection_reasons.get(exc_str, 0) + 1

    summary = {
        "symbols_count": len(data),
        "total_bars_evaluated": total_bars_evaluated,
        "signals_detected": signals_detected,
        "orders_attempted": orders_attempted,
        "orders_succeeded": orders_succeeded,
        "orders_rejected": orders_rejected,
        "rejection_reasons": rejection_reasons,
        "exceptions_count": len(exceptions_encountered),
        "sample_exceptions": exceptions_encountered[:5],
        "active_gtt_orders_end": len(adapter.active_gtt_orders),
    }
    return summary


if __name__ == "__main__":
    real_data = load_real_data()
    results = run_deep_dhan_simulation(real_data)
    print("\n" + "=" * 80)
    print("DEEP DHANHQ WALK-FORWARD TEST RESULTS (RUN 1)")
    print("=" * 80)
    print(f"Total Bars Evaluated:   {results['total_bars_evaluated']}")
    print(f"Signals Detected:       {results['signals_detected']}")
    print(f"Orders Attempted:       {results['orders_attempted']}")
    print(f"Orders Succeeded:       {results['orders_succeeded']}")
    print(f"Orders Rejected:        {results['orders_rejected']}")
    print(f"Exceptions Count:       {results['exceptions_count']}")
    print("\nBreakdown of Rejection Reasons / Exceptions:")
    for reason, count in results['rejection_reasons'].items():
        print(f"  [{count}x] {reason}")

    if results['sample_exceptions']:
        print("\nSample Exceptions Detail:")
        for exc in results['sample_exceptions']:
            print(f"  {exc['symbol']} ({exc['bar_date']}): Qty={exc['qty']}, Entry={exc['entry']}, Target={exc['target']}, Stop={exc['stop']}")
            print(f"    --> {exc['exception']}")
