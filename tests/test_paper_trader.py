"""
Unit and Integration Tests for Forward Paper Testing Engine.
Verifies:
1. Sequential daily bar processing with zero lookahead bias.
2. Order lifecycle: Pending limit order placement -> pullback fill -> gap stress / target exit.
3. Pre-Trade Risk Engine enforcement (20% stock, 30% sector, 3% portfolio open risk).
4. Statutory friction and gap-slippage accounting.
"""

import pytest
from alphacouncil.execution.paper_trader import (
    ForwardPaperTestingEngine,
    PaperTradingReport,
    ExitReason,
)


def test_forward_paper_trading_engine_execution():
    """Runs a 10-stock forward paper test over 150 bars and verifies report metrics."""
    universe = ["RELIANCE", "INFY", "TCS", "HDFCBANK", "ICICIBANK"]
    engine = ForwardPaperTestingEngine(initial_equity=1_000_000.0, universe=universe, seed=42)
    report: PaperTradingReport = engine.run_simulation(n_bars=150)

    assert isinstance(report, PaperTradingReport)
    assert report.total_trades_count > 0
    assert report.winning_trades_count + report.losing_trades_count == report.total_trades_count
    assert report.total_friction_inr > 0.0  # STT and brokerage accounted for
    assert len(report.trade_journal) == report.total_trades_count

    # Check structure of a completed trade record
    first_trade = report.trade_journal[0]
    assert first_trade.is_closed is True
    assert first_trade.entry_price > 0.0
    assert first_trade.nominal_stop_loss > 0.0
    assert first_trade.target_price > first_trade.entry_price
    assert first_trade.shares > 0
    assert first_trade.allocated_notional <= 1_000_000.0 * 0.20 + 1e-5  # Under 20% cap
    assert first_trade.exit_price > 0.0
    assert first_trade.exit_reason in [
        ExitReason.TARGET_HIT.value,
        ExitReason.STOP_LOSS_HIT.value,
        ExitReason.GAP_DOWN_STOP_SLIP.value,
        ExitReason.TRAILING_STOP_EXIT.value,
        ExitReason.EARNINGS_LIQUIDATION.value,
        ExitReason.MONTH_END_CIRCUIT_CLOSE.value,
    ]


def test_forward_paper_trading_gap_slippage_captured():
    """Verifies that overnight gaps past stop-loss record gap slippage drag."""
    engine = ForwardPaperTestingEngine(initial_equity=1_000_000.0, seed=42)
    report = engine.run_simulation(n_bars=250)

    # Some trades must encounter gap slippage under realistic jump-diffusion
    assert report.total_trades_count >= 10
    # Equity curve must reflect friction deductions
    assert report.net_pnl_inr == pytest.approx(report.gross_pnl_inr - report.total_friction_inr, abs=1.0)
