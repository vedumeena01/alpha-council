"""
AlphaCouncil Real-Market Predictive Trade Dashboard.
Scans the latest historical records of 10 liquid NSE equities,
analyzes candle patterns, structural Demand/Supply zones, trend alignment,
and predicts upcoming high-probability trade setups with exact entry, stop, and targets.
"""

import os
import json
import numpy as np
from alphacouncil.alpha.zone_engine import DemandSupplyEngine

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(REPO_ROOT, "alphacouncil", "data", "real_cache")
SYMBOLS = [
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


def run_predictive_dashboard():
    engine = DemandSupplyEngine()
    print("=" * 115)
    print("🚀 ALPHACOUNCIL REAL-MARKET PREDICTIVE TRADE DASHBOARD (LATEST REAL DATA SCAN)")
    print("=" * 115)
    print(f"{'Symbol':11} | {'CMP':9} | {'50 SMA':9} | {'Trend':7} | {'Active Fresh Demand':28} | {'R:R':5} | {'AI Prediction & Action':32}")
    print("-" * 115)

    portfolio_recommendations = []

    for sym in SYMBOLS:
        p = os.path.join(CACHE_DIR, f"{sym}_2y.json")
        if not os.path.exists(p):
            continue
        with open(p) as f:
            bars = json.load(f)

        opens = np.array([b["open"] for b in bars])
        highs = np.array([b["high"] for b in bars])
        lows = np.array([b["low"] for b in bars])
        closes = np.array([b["close"] for b in bars])
        atrs = np.array([b["atr14"] for b in bars])

        cmp = float(closes[-1])
        sma50 = float(np.mean(closes[-50:]))
        trend = "BULLISH" if cmp >= sma50 else "BEARISH"

        zones = engine.scan_for_zones(opens, highs, lows, closes, atr14=atrs)
        # Find fresh demands that are at or below CMP
        fresh_demands = [z for z in zones if z.is_demand and z.is_fresh and z.proximal_line <= cmp]

        if fresh_demands:
            latest = fresh_demands[-1]
            entry = float(latest.proximal_line)
            stop = float(latest.distal_line)
            risk = entry - stop
            target = entry + 2.0 * risk
            rrr_str = "2.0:1"
            zone_str = f"PL: ₹{entry:,.1f} | DL: ₹{stop:,.1f}"

            dist_pct = ((cmp - entry) / cmp) * 100.0
            if trend == "BULLISH":
                action = f"BUY LIMIT ₹{entry:,.1f} (Tgt ₹{target:,.1f})"
                portfolio_recommendations.append({
                    "symbol": sym,
                    "cmp": cmp,
                    "entry": entry,
                    "stop": stop,
                    "target": target,
                    "risk": risk,
                    "distance_pct": dist_pct,
                    "trend": trend,
                    "quality": "HIGH PRIORITY (Trend Aligned)",
                })
            else:
                action = f"AVOID (Counter-Trend Bearish)"
        else:
            zone_str = "No Fresh Zone Below CMP"
            rrr_str = "N/A"
            action = "WAIT (Accumulating Basing Zone)"

        print(f"{sym:11} | ₹{cmp:8.2f} | ₹{sma50:8.2f} | {trend:7} | {zone_str:28} | {rrr_str:5} | {action:32}")

    print("=" * 115)
    print("\n🎯 TOP PORTFOLIO PREDICTIVE SETUPS (ACTIONABLE FUTURE TRADES):")
    print("-" * 115)
    for rec in portfolio_recommendations:
        print(f"👉 {rec['symbol']:10} | CMP: ₹{rec['cmp']:,.2f} | Recommended Entry: ₹{rec['entry']:,.2f} (Dist: {rec['distance_pct']:.1f}%) | Stop Loss: ₹{rec['stop']:,.2f} | Target 1 (2R): ₹{rec['target']:,.2f} | Quality: {rec['quality']}")
    print("-" * 115)


if __name__ == "__main__":
    run_predictive_dashboard()
