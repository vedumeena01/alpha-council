"""
Multi-Seed Empirical Ablation Distribution Generator.
Executes the 7-Model Orthogonal Ablation Suite across N random seeds,
computing empirical medians, spreads, deflated Sharpe ratios, and paired difference statistics.
Supports --zero-friction and --tie-break flags, and saves raw per-seed data to test_results/.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
import os
from typing import Dict, List, Tuple
import numpy as np

from alphacouncil.config import AlphaCouncilConfig, StatutoryFeeConfig
from alphacouncil.data.feed import MarketDataFeed
from alphacouncil.backtest.ablation import AblationSuiteRunner


DEFAULT_SYMBOLS_5 = ["RELIANCE", "INFY", "TCS", "HDFCBANK", "ICICIBANK"]

DEFAULT_SYMBOLS_25 = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "SBIN", "BHARTIARTL",
    "ITC", "KOTAKBANK", "LT", "HINDUNILVR", "AXISBANK", "BAJFINANCE", "ASIANPAINT",
    "MARUTI", "TITAN", "SUNPHARMA", "TATAMOTORS", "ULTRACEMCO", "POWERGRID",
    "NTPC", "TATASTEEL", "M&M", "ADANIENT", "JSWSTEEL"
]

CONFIGS = [
    "alpha_Null",
    "alpha_Null_Time",
    "alpha_Null_SMC",
    "alpha_Tech",
    "alpha_Tech_Risk",
    "alpha_Tech_Fund",
    "alpha_Council",
]

CONFIG_DESCRIPTIONS = {
    "alpha_Null": "α_Null (Random Coin Flip + Vol Sizing)",
    "alpha_Null_Time": "α_Null+Time (Random Entry + PIT Filter)",
    "alpha_Null_SMC": "α_Null+SMC (Random Entry + ATR Stop)",
    "alpha_Tech": "α_Tech (Sweep Signal H1 Alone)",
    "alpha_Tech_Risk": "α_Tech+Risk (Sweep + Vol-Sizing + ATR Stop)",
    "alpha_Tech_Fund": "α_Tech+Fund (Sweep + PIT Filter + ATR Stop)",
    "alpha_Council": "α_Council (Full System: H1 + H2 + Meta + Kelly)",
}


def _run_single_seed(args: Tuple[int, List[str], int, int, bool, str]) -> Tuple[int, Dict[str, dict]]:
    """Worker task running 7 configs on a single seed."""
    s, symbols, n_bars, n_trials, zero_friction, tie_break = args
    feed = MarketDataFeed(seed=s)
    # Strict zero-drift martingale random walk (annual_drift=0.0)
    data = feed.get_multi_symbol_universe(symbols, n_bars=n_bars, annual_drift=0.0)

    if zero_friction:
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
        cfg = AlphaCouncilConfig(fees=zero_fees)
    else:
        cfg = None

    runner = AblationSuiteRunner(n_trials_logged=n_trials, seed=s, config=cfg, tie_break=tie_break)
    results = runner.run_full_suite(data)

    seed_dict = {}
    for c in CONFIGS:
        res = results[c]
        n_trades = len(res.trades)
        gross = float(sum(t.gross_pnl_inr for t in res.trades))
        friction = float(sum(t.friction_inr for t in res.trades))
        net = float(sum(t.net_pnl_inr for t in res.trades))
        wins = [t for t in res.trades if t.net_pnl_inr > 0]
        losses = [t for t in res.trades if t.net_pnl_inr <= 0]
        gross_win = sum(t.gross_pnl_inr for t in wins)
        gross_loss = abs(sum(t.gross_pnl_inr for t in losses))
        pf = gross_win / gross_loss if gross_loss > 0 else (1.0 if gross_win == 0 else 5.0)
        wr = (len(wins) / n_trades * 100.0) if n_trades > 0 else 0.0

        seed_dict[c] = {
            "trades": n_trades,
            "sharpe": float(res.metrics.sharpe_ratio),
            "dsr": float(res.metrics.deflated_sharpe_ratio),
            "gross_pnl": gross,
            "friction": friction,
            "net_pnl": net,
            "profit_factor": float(pf),
            "win_rate": float(wr),
        }
    return s, seed_dict


def run_ablation_distribution(
    symbols: List[str],
    n_bars: int = 250,
    n_seeds: int = 30,
    n_trials: int = 150,
    zero_friction: bool = False,
    tie_break: str = "stop_first",
    raw_output_path: str = None,
) -> Tuple[Dict[str, Dict[str, List[float]]], List[dict]]:
    """Runs ablation suite across N seeds in parallel and returns stats + raw records."""
    stats = {
        c: {
            "trades": [],
            "sharpe": [],
            "dsr": [],
            "profit_factor": [],
            "win_rate": [],
            "gross": [],
            "friction": [],
        }
        for c in CONFIGS
    }
    raw_records = []

    tasks = [(s, symbols, n_bars, n_trials, zero_friction, tie_break) for s in range(1, n_seeds + 1)]
    max_workers = min(os.cpu_count() or 1, 16)

    # Execute in parallel across available CPU cores
    if max_workers > 1:
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            seed_results = list(executor.map(_run_single_seed, tasks))
    else:
        seed_results = [_run_single_seed(t) for t in tasks]

    # Ensure deterministic sort by seed 1..N
    seed_results.sort(key=lambda x: x[0])

    for s, seed_dict in seed_results:
        for c in CONFIGS:
            d = seed_dict[c]
            stats[c]["trades"].append(d["trades"])
            stats[c]["sharpe"].append(d["sharpe"])
            stats[c]["dsr"].append(d["dsr"])
            stats[c]["gross"].append(d["gross_pnl"])
            stats[c]["friction"].append(d["friction"])
            stats[c]["profit_factor"].append(d["profit_factor"])
            stats[c]["win_rate"].append(d["win_rate"])

            raw_records.append({
                "seed": s,
                "config": c,
                "trades": d["trades"],
                "sharpe": round(d["sharpe"], 4),
                "dsr": round(d["dsr"], 4),
                "gross_pnl_inr": round(d["gross_pnl"], 2),
                "friction_inr": round(d["friction"], 2),
                "net_pnl_inr": round(d["net_pnl"], 2),
                "win_rate_pct": round(d["win_rate"], 2),
                "profit_factor": round(d["profit_factor"], 2),
            })

    if raw_output_path:
        os.makedirs(os.path.dirname(os.path.abspath(raw_output_path)), exist_ok=True)
        with open(raw_output_path, "w", encoding="utf-8") as f:
            json.dump(raw_records, f, indent=2)
        print(f"Saved {len(raw_records)} raw seed records to {raw_output_path}")

    return stats, raw_records


def format_markdown_table(stats: Dict[str, Dict[str, List[float]]], n_seeds: int, universe_label: str) -> str:
    """Formats markdown table for PITCH_DECK.md Slide 5."""
    lines = [
        f"### Empirical Multi-Seed Ablation Distribution ({n_seeds} Seeds on {universe_label})",
        "",
        "| Configuration | Description | Median Trades | Sharpe Min / Median / Max | Median DSR | Mean Gross PnL | Mean Friction | Win Rate | Seeds Sharpe > 0 |",
        "| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
    ]

    for c in CONFIGS:
        desc = CONFIG_DESCRIPTIONS[c]
        trades_med = int(np.median(stats[c]["trades"]))
        sh_min = float(np.min(stats[c]["sharpe"]))
        sh_med = float(np.median(stats[c]["sharpe"]))
        sh_max = float(np.max(stats[c]["sharpe"]))
        dsr_med = float(np.median(stats[c]["dsr"]))
        wr_med = float(np.median(stats[c]["win_rate"]))
        gr_mean = float(np.mean(stats[c]["gross"]))
        fr_mean = float(np.mean(stats[c]["friction"]))
        pos_sh = sum(1 for x in stats[c]["sharpe"] if x > 0)
        pos_pct = (pos_sh / n_seeds) * 100.0

        lines.append(
            f"| `{c}` | {desc} | {trades_med} | {sh_min:.2f} / **{sh_med:.2f}** / {sh_max:.2f} | {dsr_med:.4f} | ₹{gr_mean:,.0f} | ₹{fr_mean:,.0f} | {wr_med:.1f}% | {pos_sh}/{n_seeds} ({pos_pct:.0f}%) |"
        )

    return "\n".join(lines)


def format_friction_share_table(stats: Dict[str, Dict[str, List[float]]], universe_label: str) -> str:
    """Formats detailed per-config friction share breakdown."""
    lines = [
        f"### Per-Configuration Friction Share Analysis ({universe_label})",
        "",
        "| Configuration | Mean Gross PnL | Mean Friction Drag | Mean Net PnL | Friction Share of Loss |",
        "| :--- | :---: | :---: | :---: | :---: |",
    ]
    for c in CONFIGS:
        gr = float(np.mean(stats[c]["gross"]))
        fr = float(np.mean(stats[c]["friction"]))
        net = gr - fr
        if gr < 0:
            gross_loss = abs(gr)
            share_pct = (fr / (fr + gross_loss)) * 100.0
            share_str = f"{share_pct:.1f}%"
        else:
            share_str = ">100% (Gross PnL is positive; 100% of loss is statutory friction)"
        lines.append(f"| `{c}` | ₹{gr:,.0f} | ₹{fr:,.0f} | ₹{net:,.0f} | **{share_str}** |")
    return "\n".join(lines)


def print_paired_stats(stats: Dict[str, Dict[str, List[float]]], universe_name: str):
    """Computes and prints paired difference statistics across identical seeds."""
    print(f"\n--- Paired Difference Statistics ({universe_name}) ---")
    comparisons = [
        ("alpha_Tech_Risk", "alpha_Tech", "Tech_Risk - Tech"),
        ("alpha_Council", "alpha_Tech_Risk", "Council - Tech_Risk"),
    ]
    for c1, c2, label in comparisons:
        arr1 = np.array(stats[c1]["sharpe"])
        arr2 = np.array(stats[c2]["sharpe"])
        diff = arr1 - arr2
        mean_diff = float(np.mean(diff))
        se = float(np.std(diff, ddof=1) / np.sqrt(len(diff)))
        n_better = int(sum(diff > 0))
        n_total = len(diff)
        print(f"{label}: Mean Diff = {mean_diff:+.2f} (SE {se:.2f}), {n_better}/{n_total} seeds better")


def main():
    parser = argparse.ArgumentParser(description="AlphaCouncil Multi-Seed Ablation Distribution Generator")
    parser.add_argument("--seeds", type=int, default=30, help="Number of random seeds to evaluate")
    parser.add_argument("--bars", type=int, default=250, help="Bars per symbol (default 250)")
    parser.add_argument("--universe", choices=["5", "25", "both"], default="both", help="Universe size: 5, 25, or both")
    parser.add_argument("--zero-friction", action="store_true", help="Execute with zero statutory transaction friction")
    parser.add_argument("--tie-break", choices=["stop_first", "close"], default="stop_first", help="Tie-break resolution when both stop and target touched in bar")
    args = parser.parse_args()

    results_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test_results")
    suffix = "_zerofriction" if args.zero_friction else ""
    if args.tie_break != "stop_first":
        suffix += f"_{args.tie_break}"

    if args.universe == "both":
        # Universe 1: 5 symbols, 250 bars
        u1_symbols = DEFAULT_SYMBOLS_5
        u1_label = f"5 NSE Constituents, 250 bars{' (Zero Friction)' if args.zero_friction else ''}"
        u1_raw_path = os.path.join(results_dir, f"ablation_raw_seeds_5symbols{suffix}.json")
        print(f"Executing {args.seeds} seeds on {u1_label} [Tie-break: {args.tie_break}]...")
        stats1, _ = run_ablation_distribution(
            u1_symbols, n_bars=250, n_seeds=args.seeds, zero_friction=args.zero_friction,
            tie_break=args.tie_break, raw_output_path=u1_raw_path
        )
        md1 = format_markdown_table(stats1, args.seeds, u1_label)
        print("\n" + md1 + "\n")
        if not args.zero_friction:
            print(format_friction_share_table(stats1, "5 Symbols, 250 bars") + "\n")
        print_paired_stats(stats1, "5 Symbols")

        # Universe 2: 25 symbols, 500 bars
        u2_symbols = DEFAULT_SYMBOLS_25
        u2_label = f"25 NSE Constituents, 500 bars{' (Zero Friction)' if args.zero_friction else ''}"
        u2_raw_path = os.path.join(results_dir, f"ablation_raw_seeds_25symbols{suffix}.json")
        print(f"\nExecuting {args.seeds} seeds on {u2_label} [Tie-break: {args.tie_break}]...")
        stats2, _ = run_ablation_distribution(
            u2_symbols, n_bars=500, n_seeds=args.seeds, zero_friction=args.zero_friction,
            tie_break=args.tie_break, raw_output_path=u2_raw_path
        )
        md2 = format_markdown_table(stats2, args.seeds, u2_label)
        print("\n" + md2 + "\n")
        if not args.zero_friction:
            print(format_friction_share_table(stats2, "25 Symbols, 500 bars") + "\n")
        print_paired_stats(stats2, "25 Symbols")
    else:
        symbols = DEFAULT_SYMBOLS_5 if args.universe == "5" else DEFAULT_SYMBOLS_25
        u_label = f"{len(symbols)} NSE Constituents, {args.bars} bars{' (Zero Friction)' if args.zero_friction else ''}"
        raw_path = os.path.join(results_dir, f"ablation_raw_seeds_{len(symbols)}symbols{suffix}.json")
        print(f"Executing {args.seeds} seeds on {u_label} [Tie-break: {args.tie_break}]...")

        stats, _ = run_ablation_distribution(
            symbols, n_bars=args.bars, n_seeds=args.seeds, zero_friction=args.zero_friction,
            tie_break=args.tie_break, raw_output_path=raw_path
        )
        md = format_markdown_table(stats, args.seeds, u_label)
        print("\n" + md + "\n")
        if not args.zero_friction:
            print(format_friction_share_table(stats, f"{len(symbols)} Symbols") + "\n")
        print_paired_stats(stats, f"{len(symbols)} Symbols")


if __name__ == "__main__":
    main()
