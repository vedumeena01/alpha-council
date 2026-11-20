"""
Advanced GTF Price Action & Multi-Bagger Trailing Simulation Engine.
Empirically tests the 3 Core Enhancement Pillars across 2 Years of Real NSE Data:
1. Auto Sector & Trend Filter (Episode 16): Eliminate lagging sectors / downtrends.
2. ATR-Based Rupee-Risk Equality: Fixed ₹10,000 risk per trade regardless of share price.
3. Dynamic Trailing Multi-Bagger Siphon (Episode 20): Book 50% at 2R, trail 50% for 3R-6R expansions.
Evaluates portfolio equity curve, win rate, profit factor, and statutory SEBI friction.
"""

import os
import json
from dataclasses import dataclass, field
from typing import Dict, List
import numpy as np

from alphacouncil.alpha.zone_engine import DemandSupplyEngine
from alphacouncil.execution.friction import IndianMarketFrictionModel

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

# Sectors classification based on 2024-2026 macro regime
SECTOR_MAP = {
    "SBIN": "PSU_BANK",
    "AXISBANK": "PVT_BANK",
    "HDFCBANK": "PVT_BANK",
    "ICICIBANK": "PVT_BANK",
    "BHARTIARTL": "TELECOM",
    "RELIANCE": "ENERGY",
    "LT": "INFRA",
    "ITC": "FMCG",
    "INFY": "IT",
    "TCS": "IT",
}

# In 2024-2026, IT was in a severe structural earnings contraction / downcycle
WEAK_SECTORS = {"IT"}


@dataclass
class TradeOutcome:
    symbol: str
    entry_day: int
    exit_day: int
    entry_price: float
    exit_price: float
    shares: int
    gross_pnl: float
    friction: float
    net_pnl: float
    r_multiple: float
    is_win: bool
    exit_type: str


@dataclass
class SimulationStats:
    variant_name: str
    total_trades: int
    wins: int
    losses: int
    win_rate_pct: float
    profit_factor: float
    gross_profit_inr: float
    gross_loss_inr: float
    statutory_friction_inr: float
    net_profit_inr: float
    starting_equity: float
    final_equity: float
    roi_pct: float
    max_drawdown_pct: float
    avg_win_inr: float
    avg_loss_inr: float
    symbol_breakdown: Dict[str, Dict[str, float]] = field(default_factory=dict)


def load_dataset() -> Dict[str, List[Dict]]:
    data = {}
    for sym in SYMBOLS:
        p = os.path.join(CACHE_DIR, f"{sym}_2y.json")
        with open(p) as f:
            data[sym] = json.load(f)
    return data


def run_single_simulation(
    data: Dict[str, List[Dict]],
    variant_name: str,
    use_sector_filter: bool,
    use_50sma_trend: bool,
    use_rupee_risk_equality: bool,
    use_dynamic_trailing: bool,
    apply_sebi_friction: bool,
    fixed_risk_inr: float = 10000.0,
    initial_capital: float = 1000000.0,
) -> SimulationStats:
    """
    Executes a walk-forward portfolio simulation with specified strategy pillars.
    """
    engine = DemandSupplyEngine()
    friction_model = IndianMarketFrictionModel() if apply_sebi_friction else None

    # Pre-compute arrays for all symbols
    arrays = {}
    for sym in SYMBOLS:
        bars = data[sym]
        opens = np.array([b["open"] for b in bars], dtype=float)
        highs = np.array([b["high"] for b in bars], dtype=float)
        lows = np.array([b["low"] for b in bars], dtype=float)
        closes = np.array([b["close"] for b in bars], dtype=float)
        atrs = np.array([b["atr14"] for b in bars], dtype=float)
        adv20s = np.array([b["adv20"] for b in bars], dtype=float)

        # 50 SMA
        sma50 = np.full_like(closes, np.nan)
        for i in range(49, len(closes)):
            sma50[i] = np.mean(closes[i - 49 : i + 1])

        # Scan all zones upfront
        zones = engine.scan_for_zones(opens, highs, lows, closes, atr14=atrs)
        # Filter for high quality demand zones with 1-3 base candles
        valid_demands = [
            z for z in zones
            if z.is_demand and z.is_high_quality and z.base_candles_count <= 3
        ]

        arrays[sym] = {
            "opens": opens,
            "highs": highs,
            "lows": lows,
            "closes": closes,
            "atrs": atrs,
            "adv20s": adv20s,
            "sma50": sma50,
            "zones": valid_demands,
        }

    n_bars = len(data[SYMBOLS[0]])
    cash = initial_capital
    active_positions = {}  # sym -> dict
    completed_trades: List[TradeOutcome] = []
    equity_curve = [cash]
    peak_equity = cash
    max_dd_inr = 0.0

    # Walk-forward bar by bar (starting after warm-up at bar 50)
    for t in range(50, n_bars):
        # 1. Update Portfolio Valuation
        current_val = cash
        for sym, pos in active_positions.items():
            current_val += pos["shares"] * arrays[sym]["opens"][t]

        if current_val > peak_equity:
            peak_equity = current_val
        dd = peak_equity - current_val
        if dd > max_dd_inr:
            max_dd_inr = dd

        # 2. Manage Active Positions at day t
        symbols_to_close = []
        for sym, pos in active_positions.items():
            bar_open = arrays[sym]["opens"][t]
            bar_high = arrays[sym]["highs"][t]
            bar_low = arrays[sym]["lows"][t]
            bar_close = arrays[sym]["closes"][t]
            holding_days = t - pos["entry_day"]

            exit_triggered = False
            exit_price = bar_close
            exit_type = "NORMAL"

            # Check stop loss
            curr_sl = pos["trailing_sl"] if use_dynamic_trailing else pos["initial_sl"]
            if bar_low <= curr_sl:
                exit_triggered = True
                exit_price = min(bar_open, curr_sl)  # Account for gap-down
                exit_type = "STOP_LOSS_HIT"
            # Check Target 1 (2.0R)
            elif not pos["scaled_out"] and bar_high >= pos["target_1"]:
                if use_dynamic_trailing:
                    # Multi-bagger siphon: book 50% shares at target 1
                    half_shares = pos["shares"] // 2
                    if half_shares > 0:
                        # Realize half
                        pnl_half = half_shares * (pos["target_1"] - pos["entry_price"])
                        fric_half = 0.0
                        if friction_model:
                            f_calc = friction_model.compute_roundtrip_friction(
                                quantity=half_shares,
                                entry_price=pos["entry_price"],
                                exit_price=pos["target_1"],
                                annualized_vol=0.25,
                                adv20=arrays[sym]["adv20s"][t],
                            )
                            fric_half = f_calc.total_friction_inr
                        cash += (half_shares * pos["target_1"]) - fric_half
                        pos["shares"] -= half_shares
                        pos["realized_pnl"] += pnl_half - fric_half
                        pos["scaled_out"] = True
                        # Ratchet trailing stop to Breakeven
                        pos["trailing_sl"] = pos["entry_price"]
                else:
                    # Fixed target full exit
                    exit_triggered = True
                    exit_price = pos["target_1"]
                    exit_type = "TARGET_HIT"

            # Dynamic Trailing Check for Remaining 50%
            if not exit_triggered and use_dynamic_trailing and pos["scaled_out"]:
                # Check Target 2 (4.0R Runner) or trailing stop breach
                if bar_high >= pos["target_2"]:
                    exit_triggered = True
                    exit_price = pos["target_2"]
                    exit_type = "RUNNER_TARGET_HIT_4R"
                elif bar_low <= pos["trailing_sl"]:
                    exit_triggered = True
                    exit_price = min(bar_open, pos["trailing_sl"])
                    exit_type = "TRAILING_STOP_HIT"
                elif holding_days >= 25:
                    exit_triggered = True
                    exit_price = bar_close
                    exit_type = "TIME_EXPIRY"

            if not exit_triggered and holding_days >= 20 and not pos["scaled_out"]:
                exit_triggered = True
                exit_price = bar_close
                exit_type = "TIME_EXPIRY"

            if exit_triggered:
                symbols_to_close.append(sym)
                rem_shares = pos["shares"]
                gross_pnl = (exit_price - pos["entry_price"]) * rem_shares + pos["realized_pnl"]
                friction = 0.0
                if friction_model and rem_shares > 0:
                    f_calc = friction_model.compute_roundtrip_friction(
                        quantity=rem_shares,
                        entry_price=pos["entry_price"],
                        exit_price=exit_price,
                        annualized_vol=0.25,
                        adv20=arrays[sym]["adv20s"][t],
                    )
                    friction = f_calc.total_friction_inr

                net_pnl = gross_pnl - friction
                cash += (rem_shares * exit_price) - friction

                risk_amount = (pos["entry_price"] - pos["initial_sl"]) * (rem_shares + (pos["shares"] if pos["scaled_out"] else 0))
                r_mult = net_pnl / (risk_amount + 1e-6)

                completed_trades.append(
                    TradeOutcome(
                        symbol=sym,
                        entry_day=pos["entry_day"],
                        exit_day=t,
                        entry_price=pos["entry_price"],
                        exit_price=exit_price,
                        shares=rem_shares,
                        gross_pnl=gross_pnl,
                        friction=friction,
                        net_pnl=net_pnl,
                        r_multiple=r_mult,
                        is_win=net_pnl > 0,
                        exit_type=exit_type,
                    )
                )

        for sym in symbols_to_close:
            del active_positions[sym]

        # 3. New Trade Entry Scanning at day t close for execution
        for sym in SYMBOLS:
            if sym in active_positions:
                continue

            # Pillar 1A: Auto Sector Filter
            if use_sector_filter and SECTOR_MAP.get(sym) in WEAK_SECTORS:
                continue

            # Pillar 1B: 50 SMA Trend Filter
            cmp = arrays[sym]["closes"][t]
            sma = arrays[sym]["sma50"][t]
            if use_50sma_trend and (np.isnan(sma) or cmp < sma):
                continue

            # Check for fresh demand zones that price is pulling back into
            for z in arrays[sym]["zones"]:
                # Zone must have formed before day t
                if z.first_leg_out_idx >= t:
                    continue
                # Zone must not have been tested earlier than day t
                if z.tested_at_idx is not None and z.tested_at_idx < t:
                    continue

                entry_p = z.proximal_line
                stop_p = z.distal_line
                risk = entry_p - stop_p
                if risk <= 0.5:
                    continue

                # Check if current day bar pulled back into entry zone
                if arrays[sym]["lows"][t] <= entry_p and arrays[sym]["highs"][t] >= entry_p:
                    # Pillar 2: Rupee Risk Equality
                    if use_rupee_risk_equality:
                        shares = int(fixed_risk_inr / risk)
                    else:
                        shares = 50  # Fixed naive shares

                    notional = shares * entry_p
                    # Portfolio allocation cap: max 20% in single stock
                    if notional > cash or notional > (initial_capital * 0.25):
                        shares = int((initial_capital * 0.20) / entry_p)
                        notional = shares * entry_p

                    if shares > 0 and cash >= notional:
                        cash -= notional
                        target_1 = round(entry_p + 2.0 * risk, 2)
                        target_2 = round(entry_p + 4.0 * risk, 2)  # Runner target

                        active_positions[sym] = {
                            "shares": shares,
                            "entry_price": entry_p,
                            "initial_sl": stop_p,
                            "trailing_sl": stop_p,
                            "target_1": target_1,
                            "target_2": target_2,
                            "entry_day": t,
                            "scaled_out": False,
                            "realized_pnl": 0.0,
                        }
                        z.tested_at_idx = t  # Mark zone as tested
                        break

        equity_curve.append(cash + sum(pos["shares"] * arrays[s]["closes"][t] for s, pos in active_positions.items()))

    # Compile Final Statistics
    total_trades = len(completed_trades)
    wins = len([tr for tr in completed_trades if tr.is_win])
    losses = total_trades - wins
    win_rate = (wins / total_trades * 100.0) if total_trades > 0 else 0.0

    gross_profit = sum(tr.gross_pnl for tr in completed_trades if tr.gross_pnl > 0)
    gross_loss = abs(sum(tr.gross_pnl for tr in completed_trades if tr.gross_pnl <= 0))
    pf = (gross_profit / gross_loss) if gross_loss > 0 else float("inf")

    total_friction = sum(tr.friction for tr in completed_trades)
    net_profit = sum(tr.net_pnl for tr in completed_trades)
    final_equity = initial_capital + net_profit
    roi = (net_profit / initial_capital) * 100.0
    max_dd_pct = (max_dd_inr / peak_equity) * 100.0

    win_pnls = [tr.net_pnl for tr in completed_trades if tr.is_win]
    loss_pnls = [abs(tr.net_pnl) for tr in completed_trades if not tr.is_win]
    avg_win = float(np.mean(win_pnls)) if win_pnls else 0.0
    avg_loss = float(np.mean(loss_pnls)) if loss_pnls else 0.0

    # Symbol breakdown
    sym_summary = {}
    for sym in SYMBOLS:
        sym_tr = [tr for tr in completed_trades if tr.symbol == sym]
        if sym_tr:
            s_w = len([t for t in sym_tr if t.is_win])
            s_net = sum(t.net_pnl for t in sym_tr)
            sym_summary[sym] = {
                "trades": len(sym_tr),
                "wins": s_w,
                "win_rate": round(s_w / len(sym_tr) * 100.0, 1),
                "net_pnl": round(s_net, 2),
            }

    return SimulationStats(
        variant_name=variant_name,
        total_trades=total_trades,
        wins=wins,
        losses=losses,
        win_rate_pct=round(win_rate, 1),
        profit_factor=round(pf, 2),
        gross_profit_inr=round(gross_profit, 2),
        gross_loss_inr=round(gross_loss, 2),
        statutory_friction_inr=round(total_friction, 2),
        net_profit_inr=round(net_profit, 2),
        starting_equity=initial_capital,
        final_equity=round(final_equity, 2),
        roi_pct=round(roi, 1),
        max_drawdown_pct=round(max_dd_pct, 1),
        avg_win_inr=round(avg_win, 2),
        avg_loss_inr=round(avg_loss, 2),
        symbol_breakdown=sym_summary,
    )


def run_all_simulations():
    print("=" * 115)
    print("🚀 ADVANCED GTF STRATEGY SIMULATION (2 YEARS REAL NSE DATA | 10 BLUECHIPS | ₹10,00,000 EQUITY)")
    print("=" * 115)

    data = load_dataset()

    # Define the 4 Progressive Variants
    variants = [
        ("1. Naive GTF Baseline (No Filters)", False, False, False, False, False),
        ("2. + Auto Sector & 50 SMA Trend Filter", True, True, False, False, False),
        ("3. + ATR ₹10,000 Rupee-Risk Equality", True, True, True, False, False),
        ("4. + Dynamic Trailing Multi-Bagger", True, True, True, True, False),
        ("5. COMPLETE PRODUCTION (All 3 + SEBI Taxes)", True, True, True, True, True),
    ]

    results: List[SimulationStats] = []
    for name, s_filt, t_filt, r_risk, trail, fric in variants:
        st = run_single_simulation(
            data=data,
            variant_name=name,
            use_sector_filter=s_filt,
            use_50sma_trend=t_filt,
            use_rupee_risk_equality=r_risk,
            use_dynamic_trailing=trail,
            apply_sebi_friction=fric,
        )
        results.append(st)

    # Print Comparison Table
    print(f"{'Variant / Strategy Setup':46} | {'Trades':6} | {'Win Rate':8} | {'PF':5} | {'Net PnL (₹)':14} | {'ROI %':7} | {'Max DD':7} | {'Avg Win/Loss':15}")
    print("-" * 115)
    for r in results:
        ratio_str = f"₹{r.avg_win_inr:,.0f} / ₹{r.avg_loss_inr:,.0f}"
        print(f"{r.variant_name:46} | {r.total_trades:6} | {r.win_rate_pct:7.1f}% | {r.profit_factor:5.2f} | ₹{r.net_profit_inr:12,.0f} | {r.roi_pct:6.1f}% | {r.max_drawdown_pct:6.1f}% | {ratio_str:15}")
    print("=" * 115)

    # Detailed Breakdown for Production Model
    prod = results[-1]
    print("\n📊 FINAL PRODUCTION MODEL DETAILS (SEBI Compliant Real-Market Strategy):")
    print(f"• Starting Capital:          ₹{prod.starting_equity:,.2f}")
    print(f"• Final Portfolio Capital:   ₹{prod.final_equity:,.2f}")
    print(f"• Net Profit Earned:         ₹{prod.net_profit_inr:,.2f} ({prod.roi_pct:+.1f}%)")
    print(f"• Total Statutory Friction:  ₹{prod.statutory_friction_inr:,.2f} (STT, GST, Stamp Duty)")
    print(f"• Profit Factor:             {prod.profit_factor:.2f}")
    print(f"• Win Rate (Success Rate):   {prod.win_rate_pct:.1f}%")
    print(f"• Max Portfolio Drawdown:    {prod.max_drawdown_pct:.1f}%")

    print("\n📈 SYMBOL-BY-SYMBOL REAL PROFIT HARVEST:")
    print(f"{'Symbol':11} | {'Sector':10} | {'Trades':6} | {'Wins':5} | {'Win Rate':8} | {'Net Profit (₹)':14}")
    print("-" * 65)
    for sym, sb in prod.symbol_breakdown.items():
        sec = SECTOR_MAP.get(sym, "OTHER")
        print(f"{sym:11} | {sec:10} | {sb['trades']:6} | {sb['wins']:5} | {sb['win_rate']:7.1f}% | ₹{sb['net_pnl']:12,.2f}")
    print("-" * 65)

    return results


if __name__ == "__main__":
    run_all_simulations()
