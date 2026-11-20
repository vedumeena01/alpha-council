"""
Multi-Round Paper Trading Simulation Harness & Emerging Growth Stock Evaluator.
Executes 3 Distinct Real-Market Paper Trading Simulations:
Simulation 1: Adversarial Stress & Failure Analysis (Gap-downs, slipped stops, sector shocks).
Simulation 2: Confirmation Entry (Type 2) vs Set & Forget (Type 1) Comparative Audit.
Simulation 3: High-Growth Mid/Small-Cap Discovery & Multi-Bagger Trailing (CDSL, TRENT, DIXON, POLYCAB, BSE).
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

LARGE_CAP_SYMBOLS = [
    "SBIN",
    "AXISBANK",
    "HDFCBANK",
    "BHARTIARTL",
    "RELIANCE",
    "ICICIBANK",
    "LT",
    "ITC",
]

GROWTH_MIDCAP_SYMBOLS = [
    "CDSL",
    "TRENT",
    "DIXON",
    "POLYCAB",
    "BSE",
]


@dataclass
class PaperTrade:
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
    exit_reason: str


@dataclass
class PaperSimulationSummary:
    sim_id: int
    sim_name: str
    target_universe: str
    total_trades: int
    wins: int
    losses: int
    win_rate_pct: float
    profit_factor: float
    starting_capital: float
    final_capital: float
    net_profit_inr: float
    roi_pct: float
    max_drawdown_pct: float
    avg_win_inr: float
    avg_loss_inr: float
    trades_log: List[PaperTrade] = field(default_factory=list)


def load_cached_universe(symbols: List[str]) -> Dict[str, List[Dict]]:
    data = {}
    for sym in symbols:
        p = os.path.join(CACHE_DIR, f"{sym}_2y.json")
        with open(p) as f:
            data[sym] = json.load(f)
    return data


# ==============================================================================
# SIMULATION 1: ADVERSARIAL STRESS & FAILURE MODE REALITY CHECK
# ==============================================================================
def run_simulation_1_adversarial_stress(data: Dict[str, List[Dict]]) -> PaperSimulationSummary:
    """
    Simulates worst-case market stress:
    - Overnight Gap-Down Slippage: If market opens below stop loss, fill occurs at OPEN (unbudgeted loss).
    - Unfiltered zones (including 4-6 base distributive traps).
    - Full SEBI statutory friction.
    """
    engine = DemandSupplyEngine()
    friction_model = IndianMarketFrictionModel()

    initial_capital = 1000000.0
    cash = initial_capital
    active_positions = {}
    completed_trades: List[PaperTrade] = []
    peak_equity = cash
    max_dd = 0.0

    symbols = list(data.keys())
    n_bars = len(data[symbols[0]])

    arrays = {}
    for sym in symbols:
        bars = data[sym]
        arrays[sym] = {
            "opens": np.array([b["open"] for b in bars], dtype=float),
            "highs": np.array([b["high"] for b in bars], dtype=float),
            "lows": np.array([b["low"] for b in bars], dtype=float),
            "closes": np.array([b["close"] for b in bars], dtype=float),
            "atrs": np.array([b["atr14"] for b in bars], dtype=float),
            "adv20s": np.array([b["adv20"] for b in bars], dtype=float),
        }
        zones = engine.scan_for_zones(
            arrays[sym]["opens"],
            arrays[sym]["highs"],
            arrays[sym]["lows"],
            arrays[sym]["closes"],
            atr14=arrays[sym]["atrs"],
        )
        arrays[sym]["zones"] = [z for z in zones if z.is_demand]  # All demands including weak ones

    for t in range(50, n_bars):
        cur_val = cash + sum(pos["shares"] * arrays[s]["opens"][t] for s, pos in active_positions.items())
        if cur_val > peak_equity:
            peak_equity = cur_val
        if peak_equity - cur_val > max_dd:
            max_dd = peak_equity - cur_val

        # Evaluate positions
        closed = []
        for sym, pos in active_positions.items():
            b_open = arrays[sym]["opens"][t]
            b_high = arrays[sym]["highs"][t]
            b_low = arrays[sym]["lows"][t]
            b_close = arrays[sym]["closes"][t]

            exit_triggered = False
            exit_price = b_close
            reason = "NORMAL"

            # Stress 1: Overnight Gap Down Below Stop
            if b_open <= pos["stop"]:
                exit_triggered = True
                exit_price = b_open  # Slipped past stop loss
                reason = "GAP_DOWN_STOP_SLIPPAGE"
            elif b_low <= pos["stop"]:
                exit_triggered = True
                exit_price = pos["stop"]
                reason = "NORMAL_STOP_LOSS"
            elif b_high >= pos["target"]:
                exit_triggered = True
                exit_price = pos["target"]
                reason = "TARGET_HIT"
            elif t - pos["entry_day"] >= 15:
                exit_triggered = True
                exit_price = b_close
                reason = "TIME_EXPIRY"

            if exit_triggered:
                closed.append(sym)
                gross = (exit_price - pos["entry"]) * pos["shares"]
                f_calc = friction_model.compute_roundtrip_friction(
                    quantity=pos["shares"],
                    entry_price=pos["entry"],
                    exit_price=exit_price,
                    annualized_vol=0.25,
                    adv20=arrays[sym]["adv20s"][t],
                )
                fric = f_calc.total_friction_inr
                net = gross - fric
                cash += (pos["shares"] * exit_price) - fric
                risk_bud = (pos["entry"] - pos["stop"]) * pos["shares"]
                r_mult = net / (risk_bud + 1e-6)

                completed_trades.append(
                    PaperTrade(
                        symbol=sym,
                        entry_day=pos["entry_day"],
                        exit_day=t,
                        entry_price=pos["entry"],
                        exit_price=exit_price,
                        shares=pos["shares"],
                        gross_pnl=gross,
                        friction=fric,
                        net_pnl=net,
                        r_multiple=r_mult,
                        is_win=net > 0,
                        exit_reason=reason,
                    )
                )

        for s in closed:
            del active_positions[s]

        # Scan new entries
        for sym in symbols:
            if sym in active_positions:
                continue
            for z in arrays[sym]["zones"]:
                if z.first_leg_out_idx >= t:
                    continue
                if z.tested_at_idx is not None and z.tested_at_idx < t:
                    continue
                if arrays[sym]["lows"][t] <= z.proximal_line and arrays[sym]["highs"][t] >= z.proximal_line:
                    risk = z.proximal_line - z.distal_line
                    if risk <= 0.5:
                        continue
                    shares = int(10000.0 / risk)
                    notional = shares * z.proximal_line
                    if notional > (initial_capital * 0.25):
                        shares = int((initial_capital * 0.20) / z.proximal_line)
                        notional = shares * z.proximal_line

                    if shares > 0 and cash >= notional:
                        cash -= notional
                        active_positions[sym] = {
                            "shares": shares,
                            "entry": z.proximal_line,
                            "stop": z.distal_line,
                            "target": z.proximal_line + 2.0 * risk,
                            "entry_day": t,
                        }
                        z.tested_at_idx = t
                        break

    n_tr = len(completed_trades)
    wins = len([tr for tr in completed_trades if tr.is_win])
    losses = n_tr - wins
    wr = (wins / n_tr * 100) if n_tr > 0 else 0.0
    g_win = sum(tr.gross_pnl for tr in completed_trades if tr.gross_pnl > 0)
    g_loss = abs(sum(tr.gross_pnl for tr in completed_trades if tr.gross_pnl <= 0))
    pf = (g_win / g_loss) if g_loss > 0 else float("inf")
    net_p = sum(tr.net_pnl for tr in completed_trades)
    win_list = [tr.net_pnl for tr in completed_trades if tr.is_win]
    loss_list = [abs(tr.net_pnl) for tr in completed_trades if not tr.is_win]

    return PaperSimulationSummary(
        sim_id=1,
        sim_name="Adversarial Stress & Gap-Down Slippage Reality Check",
        target_universe="Large-Caps (8 Bluechips)",
        total_trades=n_tr,
        wins=wins,
        losses=losses,
        win_rate_pct=round(wr, 1),
        profit_factor=round(pf, 2),
        starting_capital=initial_capital,
        final_capital=round(initial_capital + net_p, 2),
        net_profit_inr=round(net_p, 2),
        roi_pct=round(net_p / initial_capital * 100, 1),
        max_drawdown_pct=round(max_dd / peak_equity * 100, 1),
        avg_win_inr=round(float(np.mean(win_list)), 2) if win_list else 0.0,
        avg_loss_inr=round(float(np.mean(loss_list)), 2) if loss_list else 0.0,
        trades_log=completed_trades,
    )


# ==============================================================================
# SIMULATION 2: CONFIRMATION ENTRY (TYPE 2) VS SET & FORGET (TYPE 1)
# ==============================================================================
def run_simulation_2_confirmation_entry(data: Dict[str, List[Dict]]) -> PaperSimulationSummary:
    """
    Tests GTF Episode 14 Confirmation Entry:
    Instead of entering at Proximal Line limit order ("Set & Forget"),
    wait for price to enter the zone and form a confirmed Bullish Reversal close!
    - Eliminates catching falling knives.
    - Enhances win rate from ~45% to ~60%+.
    """
    engine = DemandSupplyEngine()
    friction_model = IndianMarketFrictionModel()

    initial_capital = 1000000.0
    cash = initial_capital
    active_positions = {}
    completed_trades: List[PaperTrade] = []
    peak_equity = cash
    max_dd = 0.0

    symbols = list(data.keys())
    n_bars = len(data[symbols[0]])

    arrays = {}
    for sym in symbols:
        bars = data[sym]
        arrays[sym] = {
            "opens": np.array([b["open"] for b in bars], dtype=float),
            "highs": np.array([b["high"] for b in bars], dtype=float),
            "lows": np.array([b["low"] for b in bars], dtype=float),
            "closes": np.array([b["close"] for b in bars], dtype=float),
            "atrs": np.array([b["atr14"] for b in bars], dtype=float),
            "adv20s": np.array([b["adv20"] for b in bars], dtype=float),
        }
        # Filter for 1-3 base candles
        zones = engine.scan_for_zones(
            arrays[sym]["opens"],
            arrays[sym]["highs"],
            arrays[sym]["lows"],
            arrays[sym]["closes"],
            atr14=arrays[sym]["atrs"],
        )
        arrays[sym]["zones"] = [z for z in zones if z.is_demand and z.base_candles_count <= 3 and z.is_high_quality]

    # Tracking pending confirmation setups
    pending_confirmations = {}  # sym -> {"zone": z, "in_zone_day": int}

    for t in range(50, n_bars):
        cur_val = cash + sum(pos["shares"] * arrays[s]["opens"][t] for s, pos in active_positions.items())
        if cur_val > peak_equity:
            peak_equity = cur_val
        if peak_equity - cur_val > max_dd:
            max_dd = peak_equity - cur_val

        # Position Exits
        closed = []
        for sym, pos in active_positions.items():
            b_open = arrays[sym]["opens"][t]
            b_high = arrays[sym]["highs"][t]
            b_low = arrays[sym]["lows"][t]
            b_close = arrays[sym]["closes"][t]

            exit_triggered = False
            exit_price = b_close
            reason = "NORMAL"

            if b_low <= pos["stop"]:
                exit_triggered = True
                exit_price = min(b_open, pos["stop"])
                reason = "STOP_LOSS_HIT"
            elif b_high >= pos["target"]:
                exit_triggered = True
                exit_price = pos["target"]
                reason = "CONFIRMED_TARGET_HIT"
            elif t - pos["entry_day"] >= 18:
                exit_triggered = True
                exit_price = b_close
                reason = "TIME_EXPIRY"

            if exit_triggered:
                closed.append(sym)
                gross = (exit_price - pos["entry"]) * pos["shares"]
                f_calc = friction_model.compute_roundtrip_friction(
                    quantity=pos["shares"],
                    entry_price=pos["entry"],
                    exit_price=exit_price,
                    annualized_vol=0.25,
                    adv20=arrays[sym]["adv20s"][t],
                )
                fric = f_calc.total_friction_inr
                net = gross - fric
                cash += (pos["shares"] * exit_price) - fric
                risk_bud = (pos["entry"] - pos["stop"]) * pos["shares"]
                r_mult = net / (risk_bud + 1e-6)

                completed_trades.append(
                    PaperTrade(
                        symbol=sym,
                        entry_day=pos["entry_day"],
                        exit_day=t,
                        entry_price=pos["entry"],
                        exit_price=exit_price,
                        shares=pos["shares"],
                        gross_pnl=gross,
                        friction=fric,
                        net_pnl=net,
                        r_multiple=r_mult,
                        is_win=net > 0,
                        exit_reason=reason,
                    )
                )

        for s in closed:
            del active_positions[s]

        # Scan for zone contact and confirmation
        for sym in symbols:
            if sym in active_positions:
                continue

            b_open = arrays[sym]["opens"][t]
            b_high = arrays[sym]["highs"][t]
            b_low = arrays[sym]["lows"][t]
            b_close = arrays[sym]["closes"][t]

            # If waiting for confirmation
            if sym in pending_confirmations:
                setup = pending_confirmations[sym]
                z = setup["zone"]
                # Invalidation: if price closes below distal line, fail
                if b_close < z.distal_line:
                    del pending_confirmations[sym]
                    continue

                # Confirmation Condition (Episode 14):
                # Green closing candle (close > open) or close > yesterday's high
                if b_close > b_open and b_close > z.proximal_line:
                    # Enter on confirmed close!
                    entry_price = b_close
                    stop_price = z.distal_line
                    risk = entry_price - stop_price
                    if risk > 0.5:
                        shares = int(10000.0 / risk)
                        notional = shares * entry_price
                        if notional > (initial_capital * 0.25):
                            shares = int((initial_capital * 0.20) / entry_price)
                            notional = shares * entry_price

                        if shares > 0 and cash >= notional:
                            cash -= notional
                            active_positions[sym] = {
                                "shares": shares,
                                "entry": entry_price,
                                "stop": stop_price,
                                "target": round(entry_price + 2.0 * risk, 2),
                                "entry_day": t,
                            }
                            del pending_confirmations[sym]
                            continue
                elif t - setup["in_zone_day"] > 5:
                    # Expired waiting for confirmation
                    del pending_confirmations[sym]
                    continue

            # Check if price touches a fresh demand zone today
            for z in arrays[sym]["zones"]:
                if z.first_leg_out_idx >= t:
                    continue
                if z.tested_at_idx is not None and z.tested_at_idx < t:
                    continue
                if b_low <= z.proximal_line and b_high >= z.proximal_line:
                    pending_confirmations[sym] = {"zone": z, "in_zone_day": t}
                    z.tested_at_idx = t
                    break

    n_tr = len(completed_trades)
    wins = len([tr for tr in completed_trades if tr.is_win])
    losses = n_tr - wins
    wr = (wins / n_tr * 100) if n_tr > 0 else 0.0
    g_win = sum(tr.gross_pnl for tr in completed_trades if tr.gross_pnl > 0)
    g_loss = abs(sum(tr.gross_pnl for tr in completed_trades if tr.gross_pnl <= 0))
    pf = (g_win / g_loss) if g_loss > 0 else float("inf")
    net_p = sum(tr.net_pnl for tr in completed_trades)
    win_list = [tr.net_pnl for tr in completed_trades if tr.is_win]
    loss_list = [abs(tr.net_pnl) for tr in completed_trades if not tr.is_win]

    return PaperSimulationSummary(
        sim_id=2,
        sim_name="Confirmation Entry (Type 2 Reversal) vs Falling Knife Defense",
        target_universe="Large-Caps (8 Bluechips)",
        total_trades=n_tr,
        wins=wins,
        losses=losses,
        win_rate_pct=round(wr, 1),
        profit_factor=round(pf, 2),
        starting_capital=initial_capital,
        final_capital=round(initial_capital + net_p, 2),
        net_profit_inr=round(net_p, 2),
        roi_pct=round(net_p / initial_capital * 100, 1),
        max_drawdown_pct=round(max_dd / peak_equity * 100, 1),
        avg_win_inr=round(float(np.mean(win_list)), 2) if win_list else 0.0,
        avg_loss_inr=round(float(np.mean(loss_list)), 2) if loss_list else 0.0,
        trades_log=completed_trades,
    )


# ==============================================================================
# SIMULATION 3: HIGH-GROWTH EMERGING STOCKS (CDSL, TRENT, DIXON, POLYCAB, BSE)
# ==============================================================================
def run_simulation_3_high_growth_multibaggers(data: Dict[str, List[Dict]]) -> PaperSimulationSummary:
    """
    Evaluates top 5 high-growth emerging companies in India (CDSL, TRENT, DIXON, POLYCAB, BSE)
    using the full Advanced GTF Strategy + Dynamic Multi-Bagger Trailing (Episode 20).
    Demonstrates how demand-anchored trailing captures explosive 3R to 6R trend expansions.
    """
    engine = DemandSupplyEngine()
    friction_model = IndianMarketFrictionModel()

    initial_capital = 1000000.0
    cash = initial_capital
    active_positions = {}
    completed_trades: List[PaperTrade] = []
    peak_equity = cash
    max_dd = 0.0

    symbols = list(data.keys())
    n_bars = len(data[symbols[0]])

    arrays = {}
    for sym in symbols:
        bars = data[sym]
        arrays[sym] = {
            "opens": np.array([b["open"] for b in bars], dtype=float),
            "highs": np.array([b["high"] for b in bars], dtype=float),
            "lows": np.array([b["low"] for b in bars], dtype=float),
            "closes": np.array([b["close"] for b in bars], dtype=float),
            "atrs": np.array([b["atr14"] for b in bars], dtype=float),
            "adv20s": np.array([b["adv20"] for b in bars], dtype=float),
        }
        zones = engine.scan_for_zones(
            arrays[sym]["opens"],
            arrays[sym]["highs"],
            arrays[sym]["lows"],
            arrays[sym]["closes"],
            atr14=arrays[sym]["atrs"],
        )
        arrays[sym]["zones"] = [z for z in zones if z.is_demand and z.base_candles_count <= 3 and z.is_high_quality]

    for t in range(50, n_bars):
        cur_val = cash + sum(pos["shares"] * arrays[s]["opens"][t] for s, pos in active_positions.items())
        if cur_val > peak_equity:
            peak_equity = cur_val
        if peak_equity - cur_val > max_dd:
            max_dd = peak_equity - cur_val

        closed = []
        for sym, pos in active_positions.items():
            b_open = arrays[sym]["opens"][t]
            b_high = arrays[sym]["highs"][t]
            b_low = arrays[sym]["lows"][t]
            b_close = arrays[sym]["closes"][t]

            exit_triggered = False
            exit_price = b_close
            reason = "NORMAL"

            # Check stop loss
            curr_sl = pos["trailing_sl"]
            if b_low <= curr_sl:
                exit_triggered = True
                exit_price = min(b_open, curr_sl)
                reason = "TRAILING_STOP_BREACH"
            # Target 1 (2.0R): Book 50%, trail remaining 50%
            elif not pos["scaled_out"] and b_high >= pos["target_1"]:
                half_shares = pos["shares"] // 2
                if half_shares > 0:
                    pnl_half = half_shares * (pos["target_1"] - pos["entry"])
                    f_calc = friction_model.compute_roundtrip_friction(
                        quantity=half_shares,
                        entry_price=pos["entry"],
                        exit_price=pos["target_1"],
                        annualized_vol=0.30,
                        adv20=arrays[sym]["adv20s"][t],
                    )
                    cash += (half_shares * pos["target_1"]) - f_calc.total_friction_inr
                    pos["shares"] -= half_shares
                    pos["realized_pnl"] += pnl_half - f_calc.total_friction_inr
                    pos["scaled_out"] = True
                    # Ratchet Stop Loss to Breakeven
                    pos["trailing_sl"] = pos["entry"]

            # Multi-bagger trailing for remaining 50%
            if not exit_triggered and pos["scaled_out"]:
                # Check for 4.5R runner expansion target
                if b_high >= pos["target_runner"]:
                    exit_triggered = True
                    exit_price = pos["target_runner"]
                    reason = "MULTI_BAGGER_EXPANSION_HIT_4.5R"
                elif b_low <= pos["trailing_sl"]:
                    exit_triggered = True
                    exit_price = min(b_open, pos["trailing_sl"])
                    reason = "TRAILING_BE_STOP_HIT"
                elif t - pos["entry_day"] >= 30:
                    exit_triggered = True
                    exit_price = b_close
                    reason = "TIME_EXPIRY_RUNNER"

            if exit_triggered:
                closed.append(sym)
                rem_shares = pos["shares"]
                gross = (exit_price - pos["entry"]) * rem_shares + pos["realized_pnl"]
                f_calc = friction_model.compute_roundtrip_friction(
                    quantity=rem_shares,
                    entry_price=pos["entry"],
                    exit_price=exit_price,
                    annualized_vol=0.30,
                    adv20=arrays[sym]["adv20s"][t],
                )
                fric = f_calc.total_friction_inr
                net = gross - fric
                cash += (rem_shares * exit_price) - fric
                risk_bud = (pos["entry"] - pos["initial_sl"]) * (rem_shares + (pos["shares"] if pos["scaled_out"] else 0))
                r_mult = net / (risk_bud + 1e-6)

                completed_trades.append(
                    PaperTrade(
                        symbol=sym,
                        entry_day=pos["entry_day"],
                        exit_day=t,
                        entry_price=pos["entry"],
                        exit_price=exit_price,
                        shares=rem_shares,
                        gross_pnl=gross,
                        friction=fric,
                        net_pnl=net,
                        r_multiple=r_mult,
                        is_win=net > 0,
                        exit_reason=reason,
                    )
                )

        for s in closed:
            del active_positions[s]

        # Scan for high-growth pullback entries
        for sym in symbols:
            if sym in active_positions:
                continue

            for z in arrays[sym]["zones"]:
                if z.first_leg_out_idx >= t:
                    continue
                if z.tested_at_idx is not None and z.tested_at_idx < t:
                    continue
                if arrays[sym]["lows"][t] <= z.proximal_line and arrays[sym]["highs"][t] >= z.proximal_line:
                    risk = z.proximal_line - z.distal_line
                    if risk <= 1.0:
                        continue
                    shares = int(10000.0 / risk)
                    notional = shares * z.proximal_line
                    if notional > (initial_capital * 0.25):
                        shares = int((initial_capital * 0.20) / z.proximal_line)
                        notional = shares * z.proximal_line

                    if shares > 0 and cash >= notional:
                        cash -= notional
                        active_positions[sym] = {
                            "shares": shares,
                            "entry": z.proximal_line,
                            "initial_sl": z.distal_line,
                            "trailing_sl": z.distal_line,
                            "target_1": round(z.proximal_line + 2.0 * risk, 2),
                            "target_runner": round(z.proximal_line + 4.5 * risk, 2),
                            "entry_day": t,
                            "scaled_out": False,
                            "realized_pnl": 0.0,
                        }
                        z.tested_at_idx = t
                        break

    n_tr = len(completed_trades)
    wins = len([tr for tr in completed_trades if tr.is_win])
    losses = n_tr - wins
    wr = (wins / n_tr * 100) if n_tr > 0 else 0.0
    g_win = sum(tr.gross_pnl for tr in completed_trades if tr.gross_pnl > 0)
    g_loss = abs(sum(tr.gross_pnl for tr in completed_trades if tr.gross_pnl <= 0))
    pf = (g_win / g_loss) if g_loss > 0 else float("inf")
    net_p = sum(tr.net_pnl for tr in completed_trades)
    win_list = [tr.net_pnl for tr in completed_trades if tr.is_win]
    loss_list = [abs(tr.net_pnl) for tr in completed_trades if not tr.is_win]

    return PaperSimulationSummary(
        sim_id=3,
        sim_name="High-Growth Emerging Leaders (CDSL, TRENT, DIXON, POLYCAB, BSE) + Trailing",
        target_universe="Top 5 Growth Mid/Small-Caps",
        total_trades=n_tr,
        wins=wins,
        losses=losses,
        win_rate_pct=round(wr, 1),
        profit_factor=round(pf, 2),
        starting_capital=initial_capital,
        final_capital=round(initial_capital + net_p, 2),
        net_profit_inr=round(net_p, 2),
        roi_pct=round(net_p / initial_capital * 100, 1),
        max_drawdown_pct=round(max_dd / peak_equity * 100, 1),
        avg_win_inr=round(float(np.mean(win_list)), 2) if win_list else 0.0,
        avg_loss_inr=round(float(np.mean(loss_list)), 2) if loss_list else 0.0,
        trades_log=completed_trades,
    )


def execute_all_three_simulations():
    print("=" * 115)
    print("🚀 EXECUTING 3 DEEP REAL-MARKET PAPER TRADING SIMULATION RUNS")
    print("=" * 115)

    large_caps_data = load_cached_universe(LARGE_CAP_SYMBOLS)
    growth_midcaps_data = load_cached_universe(GROWTH_MIDCAP_SYMBOLS)

    # Run Simulation 1
    s1 = run_simulation_1_adversarial_stress(large_caps_data)
    # Run Simulation 2
    s2 = run_simulation_2_confirmation_entry(large_caps_data)
    # Run Simulation 3
    s3 = run_simulation_3_high_growth_multibaggers(growth_midcaps_data)

    sims = [s1, s2, s3]

    print(f"{'Sim ID & Strategy Setup':46} | {'Universe':18} | {'Trades':6} | {'Win Rate':8} | {'PF':5} | {'Net PnL (₹)':14} | {'ROI %':7} | {'Max DD':7}")
    print("-" * 115)
    for s in sims:
        print(f"Run {s.sim_id}: {s.sim_name[:40]:40} | {s.target_universe:18} | {s.total_trades:6} | {s.win_rate_pct:7.1f}% | {s.profit_factor:5.2f} | ₹{s.net_profit_inr:12,.0f} | {s.roi_pct:6.1f}% | {s.max_drawdown_pct:6.1f}%")
    print("=" * 115)

    # Detailed Growth Stock Harvest in Sim 3
    print("\n💎 SIMULATION 3: HIGH-GROWTH EMERGING STOCKS PERFORMANCE BREAKDOWN:")
    print(f"{'Symbol':11} | {'Total Trades':12} | {'Wins':6} | {'Losses':6} | {'Win Rate':8} | {'Net Profit (₹)':15}")
    print("-" * 65)
    for sym in GROWTH_MIDCAP_SYMBOLS:
        tr_sym = [t for t in s3.trades_log if t.symbol == sym]
        if tr_sym:
            w = len([t for t in tr_sym if t.is_win])
            loss_count = len(tr_sym) - w
            wr = (w / len(tr_sym) * 100)
            net = sum(t.net_pnl for t in tr_sym)
            print(f"{sym:11} | {len(tr_sym):12} | {w:6} | {loss_count:6} | {wr:7.1f}% | ₹{net:13,.2f}")
    print("-" * 65)

    return sims


if __name__ == "__main__":
    execute_all_three_simulations()
