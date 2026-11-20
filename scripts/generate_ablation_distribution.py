"""
Multi-Seed Empirical Ablation Distribution Generator.
Executes the 7-Model Orthogonal Ablation Suite across N random seeds,
computing empirical medians, spreads, and deflated Sharpe ratios without cherry-picking.
"""

import argparse
from typing import Dict, List
import numpy as np

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


def run_ablation_distribution(
    symbols: List[str],
    n_bars: int = 250,
    n_seeds: int = 30,
    n_trials: int = 150,
) -> Dict[str, Dict[str, List[float]]]:
    """Runs ablation suite across N seeds and returns structured stats."""
    stats = {c: {"trades": [], "sharpe": [], "dsr": [], "profit_factor": [], "win_rate": []} for c in CONFIGS}

    for s in range(1, n_seeds + 1):
        feed = MarketDataFeed(seed=s)
        data = feed.get_multi_symbol_universe(symbols, n_bars=n_bars)
        runner = AblationSuiteRunner(n_trials_logged=n_trials, seed=s)
        results = runner.run_full_suite(data)

        for c in CONFIGS:
            res = results[c]
            n_trades = len(res.trades)
            stats[c]["trades"].append(n_trades)
            stats[c]["sharpe"].append(res.metrics.sharpe_ratio)
            stats[c]["dsr"].append(res.metrics.deflated_sharpe_ratio)

            # Profit factor & win rate
            wins = [t for t in res.trades if t.net_pnl_inr > 0]
            losses = [t for t in res.trades if t.net_pnl_inr <= 0]
            gross_win = sum(t.gross_pnl_inr for t in wins)
            gross_loss = abs(sum(t.gross_pnl_inr for t in losses))
            pf = gross_win / gross_loss if gross_loss > 0 else (1.0 if gross_win == 0 else 5.0)
            wr = (len(wins) / n_trades * 100.0) if n_trades > 0 else 0.0

            stats[c]["profit_factor"].append(pf)
            stats[c]["win_rate"].append(wr)

    return stats


def format_markdown_table(stats: Dict[str, Dict[str, List[float]]], n_seeds: int, universe_label: str) -> str:
    """Formats markdown table for PITCH_DECK.md Slide 5."""
    lines = [
        f"### Empirical Multi-Seed Ablation Distribution ({n_seeds} Seeds on {universe_label})",
        "",
        "| Configuration | Description | Median Trades | Sharpe Min / Median / Max | Median DSR | Win Rate Med | PF Med | Seeds Sharpe > 0 |",
        "| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |",
    ]

    for c in CONFIGS:
        desc = CONFIG_DESCRIPTIONS[c]
        trades_med = int(np.median(stats[c]["trades"]))
        sh_min = float(np.min(stats[c]["sharpe"]))
        sh_med = float(np.median(stats[c]["sharpe"]))
        sh_max = float(np.max(stats[c]["sharpe"]))
        dsr_med = float(np.median(stats[c]["dsr"]))
        wr_med = float(np.median(stats[c]["win_rate"]))
        pf_med = float(np.median(stats[c]["profit_factor"]))
        pos_sh = sum(1 for x in stats[c]["sharpe"] if x > 0)
        pos_pct = (pos_sh / n_seeds) * 100.0

        lines.append(
            f"| `{c}` | {desc} | {trades_med} | {sh_min:.2f} / **{sh_med:.2f}** / {sh_max:.2f} | {dsr_med:.4f} | {wr_med:.1f}% | {pf_med:.2f} | {pos_sh}/{n_seeds} ({pos_pct:.0f}%) |"
        )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="AlphaCouncil Multi-Seed Ablation Distribution Generator")
    parser.add_argument("--seeds", type=int, default=30, help="Number of random seeds to evaluate")
    parser.add_argument("--bars", type=int, default=250, help="Bars per symbol (default 250)")
    parser.add_argument("--universe", choices=["5", "25"], default="5", help="Universe size: 5 or 25 symbols")
    args = parser.parse_args()

    symbols = DEFAULT_SYMBOLS_5 if args.universe == "5" else DEFAULT_SYMBOLS_25
    u_label = f"{len(symbols)} NSE Constituents, {args.bars} bars"
    print(f"Executing {args.seeds} seeds on {u_label}...")

    stats = run_ablation_distribution(symbols, n_bars=args.bars, n_seeds=args.seeds)
    md = format_markdown_table(stats, args.seeds, u_label)
    print("\n" + md)


if __name__ == "__main__":
    main()
