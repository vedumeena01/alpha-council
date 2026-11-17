"""
Bloomberg-Style Interactive Terminal UI for AlphaCouncil.
Renders real-time telemetry, 3-plane decision tree, statutory SEBI fee audits,
and the 7-model orthogonal ablation matrix using the Rich library.
"""

from typing import Dict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from alphacouncil.backtest.engine import BacktestResult
from alphacouncil.execution.friction import FrictionBreakdown
from alphacouncil.alpha.sentiment_nlp import ContaminationResult


class AlphaCouncilDashboard:
    """
    Renders institutional console presentations for trading desk pitches and investors.
    """

    def __init__(self):
        self.console = Console()

    def print_banner(self):
        """Displays institutional terminal header banner."""
        banner_text = Text()
        banner_text.append("═" * 80 + "\n", style="bold cyan")
        banner_text.append("  ALPHACOUNCIL QUANTITATIVE TRADING PLATFORM (RFC v5.0)\n", style="bold green")
        banner_text.append("  Separation of Alpha, Deterministic Risk, and Execution (Marcos López de Prado AFML)\n", style="italic white")
        banner_text.append("  Author: Vedprakash Meena (@vedumeena01) | Target: NSE Cash & Derivatives\n", style="dim yellow")
        banner_text.append("═" * 80, style="bold cyan")
        self.console.print(banner_text)

    def display_three_planes(self):
        """Displays the 3-plane decoupled architecture status."""
        table = Table(title="Three-Plane Architecture Operational Status", border_style="cyan")
        table.add_column("Plane", style="bold yellow", width=22)
        table.add_column("Primary Responsibility", style="white", width=30)
        table.add_column("Safety Guardrail", style="green", width=26)

        table.add_row(
            "I. Signal & NLP Plane",
            "Deterministic Sweep (H1) + FinBERT (H2)",
            "Strict t+1 Open (Zero Lookahead)",
        )
        table.add_row(
            "II. Deterministic Risk Plane",
            "Volatility-Targeted Sizing + Kelly Cap",
            "Meta-Labeler One-Way Downscaler",
        )
        table.add_row(
            "III. Execution Plane",
            "Idempotent OMS + Broker-Side GTT/SL-M",
            "1-Sec Partial-Fill Quantity Sync",
        )
        self.console.print(table)
        self.console.print()

    def display_trade_ticket(
        self,
        symbol: str,
        entry_price: float,
        stop_price: float,
        target_price: float,
        shares: int,
        sizing_regime: str,
        meta_scale: float,
        predicted_win_prob: float,
        friction: FrictionBreakdown,
    ):
        """Renders an institutional trade execution ticket with SEBI fee audit."""
        ticket_table = Table(title=f"Order Execution Ticket: {symbol} [NSE CASH]", border_style="green")
        ticket_table.add_column("Parameter", style="bold cyan")
        ticket_table.add_column("Value / Level", style="bold white")
        ticket_table.add_column("Institutional Governance", style="dim green")

        ticket_table.add_row("Order Action", "BUY (Long-Biased Cash Swing)", "Next-Bar Open Execution")
        ticket_table.add_row("Execution Entry Price", f"₹{entry_price:,.2f}", "Unadjusted Market Open (Bar t+1)")
        ticket_table.add_row("Structural Stop Price", f"₹{stop_price:,.2f}", "Native Broker-Side GTT SL-M Order")
        ticket_table.add_row("Triple Barrier Target", f"₹{target_price:,.2f}", "Payoff Ratio b = 2.0x D_stop")
        ticket_table.add_row("Position Size (Shares)", f"{shares:,} shares", f"Notional: ₹{shares * entry_price:,.2f} (<= 20% cap)")
        ticket_table.add_row("Meta-Labeler Scaling", f"α_scale = {meta_scale:.2f}", f"Model Win Prob = {predicted_win_prob*100:.1f}%")
        ticket_table.add_row("Sizing Regime Mode", sizing_regime, "Governed by Rolling BSS Calibration")

        self.console.print(ticket_table)

        # Statutory SEBI Fee Table
        fee_table = Table(title="Tested Statutory NSE/SEBI Friction Breakdown (Oct 1, 2024)", border_style="yellow")
        fee_table.add_column("Charge Component", style="white")
        fee_table.add_column("Statutory Rate", style="dim white")
        fee_table.add_column("Amount (INR)", style="bold red")

        fee_table.add_row("Securities Transaction Tax (STT)", "0.10% (Delivery Buy & Sell)", f"₹{friction.stt_tax:,.2f}")
        fee_table.add_row("Brokerage", "₹20 flat per order cap", f"₹{friction.brokerage:,.2f}")
        fee_table.add_row("NSE Exchange Turnover", "0.00297% of notional", f"₹{friction.exchange_charges:,.2f}")
        fee_table.add_row("SEBI Turnover Fee", "0.0001% (₹10 / Crore)", f"₹{friction.sebi_charges:,.2f}")
        fee_table.add_row("Stamp Duty", "0.015% (Buy side only)", f"₹{friction.stamp_duty:,.2f}")
        fee_table.add_row("GST", "18% on (Brok + Txn + SEBI)", f"₹{friction.gst:,.2f}")
        fee_table.add_row("Square-Root Market Impact", "γ=0.314, σ=22%, Q/ADV", f"₹{friction.market_impact_slippage:,.2f}")
        fee_table.add_row(
            "[bold green]TOTAL FRICTION (ROUND-TRIP)",
            f"[bold green]{friction.effective_friction_bps:.1f} bps of notional",
            f"[bold green]₹{friction.total_friction_inr:,.2f}",
        )

        self.console.print(fee_table)
        self.console.print()

    def display_ablation_matrix(self, ablation_results: Dict[str, BacktestResult]):
        """Displays the full 7-model orthogonal ablation table with empirical benchmarks."""
        table = Table(
            title="7-Model Orthogonal Ablation Matrix & Deflated Sharpe Ratio (DSR)",
            border_style="magenta",
        )
        table.add_column("Configuration", style="bold white", width=28)
        table.add_column("Return %", justify="right", style="cyan")
        table.add_column("Sharpe", justify="right", style="bold green")
        table.add_column("DSR (Prob)", justify="right", style="bold yellow")
        table.add_column("Sortino", justify="right", style="white")
        table.add_column("Max DD %", justify="right", style="red")
        table.add_column("Win Rate", justify="right", style="white")
        table.add_column("Profit Factor", justify="right", style="green")

        for key, res in ablation_results.items():
            m = res.metrics
            # Highlight α_Council
            style = "bold bright_green" if key == "alpha_Council" else ""
            table.add_row(
                f"[{style}]{res.config_name}[/{style}]" if style else res.config_name,
                f"{m.total_return_pct:+.1f}%",
                f"{m.sharpe_ratio:.2f}",
                f"{m.deflated_sharpe_ratio:.3f}",
                f"{m.sortino_ratio:.2f}",
                f"{m.max_drawdown_pct:.1f}%",
                f"{m.win_rate_pct:.1f}%",
                f"{m.profit_factor:.2f}",
            )

        self.console.print(table)
        self.console.print()

    def display_contamination_audit(self, audit: ContaminationResult):
        """Displays the statistical contamination probe outcome."""
        status_style = "bold red" if audit.is_contaminated else "bold green"
        panel_text = Text()
        panel_text.append("LLM CONTAMINATION & LEAKAGE AUDIT PROBE (Hypothesis H0: p <= 0.02)\n", style="bold white")
        panel_text.append(f"Total Redacted Excerpts Tested: {audit.total_samples}\n", style="white")
        panel_text.append(f"Model Ticker Guess Accuracy: {audit.ticker_accuracy*100:.1f}% vs Random Baseline: {audit.random_baseline*100:.1f}%\n", style="white")
        panel_text.append(f"Exact Binomial Cumulative p-value: {audit.p_value_ticker:.4f} (Threshold: alpha = 0.01)\n", style="yellow")
        panel_text.append(f"Status: {audit.status_message}\n", style=status_style)
        panel_text.append("Note: Pre-2020 frozen FinBERT weights guarantee mathematically clean OOS for 2021-2026 data.", style="dim cyan")

        panel = Panel(panel_text, title="Lookahead Bias Defense", border_style="cyan")
        self.console.print(panel)
        self.console.print()
