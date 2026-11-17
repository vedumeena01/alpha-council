"""
Unit Tests for Pre-Trade Risk Engine, Sizing, and Kill Switch.
"""

from alphacouncil.risk.pre_trade import PreTradeRiskEngine
from alphacouncil.risk.sizing import PositionSizingEngine
from alphacouncil.risk.kill_switch import IntradayKillSwitch
from alphacouncil.risk.circuits import CircuitBandGuard


def test_pre_trade_risk_fail_closed_on_zero_equity():
    engine = PreTradeRiskEngine()
    res = engine.validate_order(
        symbol="INFY",
        proposed_quantity=100,
        entry_price=1800.0,
        current_equity=0.0,  # Unresolved account
    )
    assert not res.is_approved
    assert "FAIL_CLOSED" in res.reason


def test_pre_trade_risk_single_stock_notional_cap():
    engine = PreTradeRiskEngine(max_single_stock_pct=0.20)
    equity = 1_000_000.0  # ₹10 Lakhs, max 20% = ₹2 Lakhs
    entry_price = 1000.0

    # Propose ₹4 Lakhs (400 shares) -> Must be capped to 200 shares
    res = engine.validate_order(
        symbol="TCS",
        proposed_quantity=400,
        entry_price=entry_price,
        current_equity=equity,
    )
    assert res.is_approved
    assert res.adjusted_quantity == 200
    assert "APPROVED_WITH_CAPPING" in res.reason


def test_sizing_invalidation_noise_trap_skipped():
    engine = PositionSizingEngine(min_atr_multiple=1.0)
    # Entry 1000, Stop 995 -> stop_distance = 5.0
    # ATR = 10.0 -> stop_distance < 1.0 * ATR -> skipped
    res = engine.compute_size(
        symbol="RELIANCE",
        entry_price=1000.0,
        stop_price=995.0,
        target_price=1020.0,
        atr14=10.0,
        realized_annual_vol=0.20,
        current_equity=10_000_000.0,
    )
    assert res.is_noise_trap_skipped
    assert res.shares_quantity == 0
    assert res.regime_mode == "NOISE_TRAP_SKIPPED"


def test_sizing_cold_start_and_defensive_modes():
    engine = PositionSizingEngine()

    # Cold start (<200 trades)
    res_cold = engine.compute_size(
        symbol="RELIANCE",
        entry_price=1000.0,
        stop_price=980.0,  # 20 stop distance
        target_price=1040.0,
        atr14=15.0,
        realized_annual_vol=0.15,
        current_equity=10_000_000.0,
        historical_closed_trades_count=100,
    )
    assert res_cold.regime_mode == "COLD_START"
    assert res_cold.shares_quantity > 0

    # Defensive mode (BSS <= 0)
    res_def = engine.compute_size(
        symbol="RELIANCE",
        entry_price=1000.0,
        stop_price=980.0,
        target_price=1040.0,
        atr14=15.0,
        realized_annual_vol=0.15,
        current_equity=10_000_000.0,
        historical_closed_trades_count=250,
        rolling_bss=-0.05,  # Uncalibrated
    )
    assert res_def.regime_mode == "DEFENSIVE"
    assert res_def.tau_effective == 0.005  # Halved from 1% to 0.5%


def test_circuit_proximity_long_ingress_blocked():
    guard = CircuitBandGuard(proximity_threshold_pct=0.015)
    # Upper circuit is 1000.0. Current price is 990.0 (1% distance <= 1.5%)
    res = guard.evaluate_long_position(
        current_price=990.0,
        upper_circuit=1000.0,
        lower_circuit=800.0,
        is_entry=True,
    )
    assert not res.can_enter
    assert "ENTRY_BLOCKED" in res.reason


def test_intraday_kill_switch_halt_on_2_percent():
    switch = IntradayKillSwitch(intraday_halt_threshold=0.02)
    switch.reset_daily_session(10_000_000.0)

    # Drops to 9,750,000 (2.5% drawdown)
    status = switch.update_valuation(9_750_000.0)
    assert status.is_session_halted
    assert "SESSION_HALTED" in status.action_taken
