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

    # Defensive mode (BSS <= 0, trades >= 200, estimated_win_prob provided)
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
        estimated_win_prob=0.55,
    )
    assert res_def.regime_mode == "DEFENSIVE"
    assert res_def.tau_effective == 0.005  # Halved from 1% to 0.5%


def test_sizing_nan_fail_closed():
    engine = PositionSizingEngine()
    # NaN ATR must fail closed, not skip noise trap and size up!
    res_nan = engine.compute_size(
        symbol="RELIANCE",
        entry_price=1000.0,
        stop_price=980.0,
        target_price=1040.0,
        atr14=float("nan"),
        realized_annual_vol=0.15,
        current_equity=10_000_000.0,
    )
    assert res_nan.is_aborted
    assert res_nan.shares_quantity == 0
    assert "Fail-closed" in res_nan.rationale


def test_pre_trade_reduce_only_bypasses_limits():
    engine = PreTradeRiskEngine(max_single_stock_pct=0.20, max_orders_per_sec=2)
    # Fill rate limiter with 2 orders
    engine.validate_order("TCS", 10, 1000.0, 1_000_000.0)
    engine.validate_order("TCS", 10, 1000.0, 1_000_000.0)

    # 3rd entry order blocked by rate limiter
    entry_val = engine.validate_order("TCS", 10, 1000.0, 1_000_000.0)
    assert not entry_val.is_approved
    assert entry_val.rejection_code == "ERR_RATE_LIMIT"

    # Reduce-only exit order MUST NEVER be blocked by rate limiter or concentration!
    exit_val = engine.validate_order(
        symbol="TCS",
        proposed_quantity=50,
        entry_price=1000.0,
        current_equity=1_000_000.0,
        current_position_shares=50,
        is_reduce_only=True,
    )
    assert exit_val.is_approved
    assert exit_val.adjusted_quantity == 50
    assert "REDUCE_ONLY_PASSED" in exit_val.reason


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

    # Lower circuit is 800.0. Current price is 808.0 (1% distance <= 1.5%) -> must also be blocked on entry
    res_lower = guard.evaluate_long_position(
        current_price=808.0,
        upper_circuit=1000.0,
        lower_circuit=800.0,
        is_entry=True,
    )
    assert not res_lower.can_enter
    assert "Lower Circuit" in res_lower.reason


def test_intraday_kill_switch_halt_on_2_percent():
    switch = IntradayKillSwitch(intraday_halt_threshold=0.02, monthly_freeze_threshold=0.06)
    switch.reset_daily_session(10_000_000.0)

    # Drops to 9,750,000 (2.5% drawdown)
    status = switch.update_valuation(9_750_000.0)
    assert status.is_session_halted
    assert "SESSION_HALTED" in status.action_taken

    # Drops to 9,300,000 (7.0% drawdown) -> Monthly strategy freeze
    status_freeze = switch.update_valuation(9_300_000.0)
    assert status_freeze.is_strategy_frozen

    # Committee unfreezes after audit
    switch.risk_committee_unfreeze(authorized_by="Chief_Risk_Officer", reason="Circuit breaker audit cleared")
    assert not switch.is_strategy_frozen
    assert not switch.is_session_halted
