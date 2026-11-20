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
    engine = PositionSizingEngine(cold_start_trade_threshold=50)

    # Cold start (<50 trades, even if BSS and win prob provided)
    res_cold = engine.compute_size(
        symbol="RELIANCE",
        entry_price=1000.0,
        stop_price=980.0,  # 20 stop distance
        target_price=1040.0,
        atr14=15.0,
        realized_annual_vol=0.15,
        current_equity=10_000_000.0,
        historical_closed_trades_count=25,
        rolling_bss=0.12,
        estimated_win_prob=0.60,
    )
    assert res_cold.regime_mode == "COLD_START"
    assert res_cold.shares_quantity > 0

    # Defensive mode (BSS <= 0, trades >= threshold, estimated_win_prob provided)
    res_def = engine.compute_size(
        symbol="RELIANCE",
        entry_price=1000.0,
        stop_price=980.0,
        target_price=1040.0,
        atr14=15.0,
        realized_annual_vol=0.15,
        current_equity=10_000_000.0,
        historical_closed_trades_count=60,
        rolling_bss=-0.05,  # Uncalibrated
        estimated_win_prob=0.55,
    )
    assert res_def.regime_mode == "DEFENSIVE"
    assert res_def.tau_effective == 0.005  # Halved from 1% to 0.5%


def test_sizing_calibrated_kelly_transition():
    engine = PositionSizingEngine(cold_start_trade_threshold=50)
    # Calibrated Kelly mode (BSS > 0, trades >= 50, valid edge)
    res_kelly = engine.compute_size(
        symbol="RELIANCE",
        entry_price=1000.0,
        stop_price=980.0,
        target_price=1040.0,
        atr14=15.0,
        realized_annual_vol=0.15,
        current_equity=10_000_000.0,
        historical_closed_trades_count=60,
        rolling_bss=0.12,  # Calibrated predictive skill!
        estimated_win_prob=0.60,
    )
    assert res_kelly.regime_mode == "CALIBRATED_KELLY"
    assert res_kelly.shares_quantity > 0


def test_sizing_production_mode_enforces_200_threshold():
    from alphacouncil.config import PROD_THRESHOLD

    # Production mode enforces cold_start_trade_threshold = 200
    engine_prod = PositionSizingEngine(is_production=True)
    assert engine_prod.cold_start_trade_threshold == PROD_THRESHOLD

    # 60 trades is still COLD_START under production mode (< 200)
    res_cold = engine_prod.compute_size(
        symbol="RELIANCE",
        entry_price=1000.0,
        stop_price=980.0,
        target_price=1040.0,
        atr14=15.0,
        realized_annual_vol=0.15,
        current_equity=10_000_000.0,
        historical_closed_trades_count=60,
        rolling_bss=0.12,
        estimated_win_prob=0.60,
    )
    assert res_cold.regime_mode == "COLD_START"

    # Crosses 200 trades -> transitions to CALIBRATED_KELLY
    res_cal = engine_prod.compute_size(
        symbol="RELIANCE",
        entry_price=1000.0,
        stop_price=980.0,
        target_price=1040.0,
        atr14=15.0,
        realized_annual_vol=0.15,
        current_equity=10_000_000.0,
        historical_closed_trades_count=205,
        rolling_bss=0.12,
        estimated_win_prob=0.60,
    )
    assert res_cal.regime_mode == "CALIBRATED_KELLY"


def test_sizing_production_mode_rejects_sub_200_override():
    import pytest
    from alphacouncil.config import PROD_THRESHOLD

    # Explicit threshold >= PROD_THRESHOLD is allowed in production
    eng_ok = PositionSizingEngine(is_production=True, cold_start_trade_threshold=250)
    assert eng_ok.cold_start_trade_threshold == 250

    # Overriding to < PROD_THRESHOLD in production must raise ValueError
    with pytest.raises(ValueError, match="Production mode requires at least PROD_THRESHOLD"):
        PositionSizingEngine(is_production=True, cold_start_trade_threshold=10)

    # In non-production (e.g. test harness), overriding < 200 is allowed
    eng_harness = PositionSizingEngine(is_production=False, cold_start_trade_threshold=10)
    assert eng_harness.cold_start_trade_threshold == 10


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

    # Reduce-only exit order MUST NEVER be blocked by rate limiter, sector cap, or open risk!
    exit_val = engine.validate_order(
        symbol="TCS",
        proposed_quantity=50,
        entry_price=1000.0,
        current_equity=1_000_000.0,
        current_position_shares=50,
        is_reduce_only=True,
        current_sector_notional=500_000.0,  # 50% sector exposure (would block entry)
        current_portfolio_open_risk_pct=0.05,  # 5.0% open risk (would block entry)
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


def test_pre_trade_risk_sector_concentration_cap_30_pct():
    """Verifies that proposed order is rejected if sector notional exposure exceeds 30%."""
    engine = PreTradeRiskEngine(max_sector_pct=0.30)
    equity = 1_000_000.0  # ₹10 Lakhs, max sector = ₹3 Lakhs

    # Existing banking sector notional = ₹2.5 Lakhs. Proposed HDFCBANK = ₹1.0 Lakh (Total = ₹3.5 Lakhs > ₹3.0 Lakhs)
    res = engine.validate_order(
        symbol="HDFCBANK",
        proposed_quantity=60,
        entry_price=1600.0,  # ₹96,000 notional
        current_equity=equity,
        current_sector_notional=250_000.0,
    )
    assert not res.is_approved
    assert "SECTOR_CONCENTRATION_EXCEEDED" in res.reason


def test_pre_trade_risk_portfolio_max_concurrent_open_risk_cap_3_pct():
    """Verifies that portfolio open risk is hard-capped at 3.0% across all concurrent positions."""
    engine = PreTradeRiskEngine(max_total_open_risk_pct=0.03)
    equity = 1_000_000.0

    # Current open risk = 2.5%. Proposed trade risk = 1.0% (Total = 3.5% > 3.0%)
    res = engine.validate_order(
        symbol="SBIN",
        proposed_quantity=100,
        entry_price=800.0,
        stop_loss_price=700.0,  # Risk = 100 * 100 = ₹10,000 (1.0%)
        current_equity=equity,
        current_portfolio_open_risk_pct=0.025,
    )
    assert not res.is_approved
    assert "PORTFOLIO_RISK_CAP_EXCEEDED" in res.reason


def test_pre_trade_risk_gap_stress_testing_2x_stop_slippage():
    """Verifies that position sizing scales down if a 2x stop gap-down exceeds 2.0% equity tolerance."""
    engine = PreTradeRiskEngine()
    equity = 1_000_000.0  # Max gap-stress loss allowed = 2.0% = ₹20,000

    # Entry 1000, Stop 900 (Risk per share = ₹100, 2x gap-stress = ₹200/share)
    # Proposed 200 shares -> Stressed loss = 200 * ₹200 = ₹40,000 (> ₹20,000)
    # Must be capped to 100 shares!
    res = engine.validate_order(
        symbol="TATASTEEL",
        proposed_quantity=200,
        entry_price=1000.0,
        stop_loss_price=900.0,
        current_equity=equity,
        max_gap_stress_pct=0.02,
    )
    assert res.is_approved
    assert res.adjusted_quantity == 100
    assert "GAP_STRESS_APPLIED" in res.reason


def test_pre_trade_risk_single_stock_capping_does_not_bypass_sector_cap():
    """
    CRITICAL FIX VERIFICATION:
    If 20% single-stock notional cap binds, it must NOT return early and bypass
    the downstream sector concentration, open risk, or gap stress gates!
    """
    engine = PreTradeRiskEngine(max_single_stock_pct=0.20, max_sector_pct=0.30)
    equity = 1_000_000.0  # Max single stock = ₹2L, max sector = ₹3L

    # Existing IT sector exposure = ₹2.5L (25%).
    # Proposed INFY order: 400 shares @ ₹1000 = ₹4L (exceeds single stock 20%).
    # If capped to 200 shares (₹2L), total sector notional would be ₹2.5L + ₹2.0L = ₹4.5L (> ₹3L ceiling)!
    # Previously, early return approved 200 shares bypassing the sector cap.
    # Now, sector cap must catch it and reject or enforce the sector ceiling!
    res = engine.validate_order(
        symbol="INFY",
        proposed_quantity=400,
        entry_price=1000.0,
        current_equity=equity,
        current_sector_notional=250_000.0,
    )
    assert not res.is_approved
    assert "SECTOR_CONCENTRATION_EXCEEDED" in res.reason


def test_kill_switch_sticky_session_halt():
    """
    Verifies that once an intraday session halt triggers (drawdown >= 2%),
    the halt remains sticky for the rest of the day even if mid-market equity rebounds.
    """
    switch = IntradayKillSwitch(intraday_halt_threshold=0.02)
    switch.reset_daily_session(1_000_000.0)

    # 1. Equity drops to 975,000 (2.5% drawdown) -> Halted
    s1 = switch.update_valuation(975_000.0)
    assert s1.is_session_halted

    # 2. Equity rebounds intraday to 990,000 (1.0% drawdown) -> Must REMAIN halted!
    s2 = switch.update_valuation(990_000.0)
    assert s2.is_session_halted
    assert "SESSION_HALTED" in s2.action_taken

    # 3. Next day 9:00 AM reset clears the halt
    switch.reset_daily_session(990_000.0)
    s3 = switch.update_valuation(990_000.0)
    assert not s3.is_session_halted


def test_kill_switch_monthly_reset_does_not_instant_rehalt():
    """
    Verifies that reset_monthly_session re-anchors both monthly_hwm and intraday_hwm
    so that a portfolio entering a new month in drawdown does not instantly trigger a daily halt.
    """
    switch = IntradayKillSwitch(intraday_halt_threshold=0.02, monthly_freeze_threshold=0.06)
    switch.reset_daily_session(1_000_000.0)

    # Experienced a 5.0% drawdown in Month 1 (equity = 950,000)
    switch.update_valuation(950_000.0)

    # Month rollover: reset_monthly_session called with current equity 950,000
    switch.reset_monthly_session(950_000.0)
    assert switch.intraday_hwm == 950_000.0
    assert switch.monthly_hwm == 950_000.0

    # Valuation check at 950,000 must be NOMINAL, NOT halted!
    s_new = switch.update_valuation(950_000.0)
    assert not s_new.is_session_halted
    assert not s_new.is_strategy_frozen
    assert s_new.intraday_drawdown_pct == 0.0


def test_kill_switch_risk_committee_audit_log():
    """
    Verifies that unfreezing produces an immutable, audit-trailed RiskAuditRecord.
    """
    switch = IntradayKillSwitch(monthly_freeze_threshold=0.06)
    switch.reset_daily_session(1_000_000.0)
    switch.update_valuation(930_000.0)  # 7% drawdown -> Frozen

    assert switch.is_strategy_frozen

    record = switch.risk_committee_unfreeze(
        authorized_by="ChiefRiskOfficer_ID_8842",
        reason="Macro volatility event resolved; capital allocated for defensive resumption.",
        current_equity=930_000.0,
    )
    assert len(switch.audit_log) >= 1
    assert record.authorized_by == "ChiefRiskOfficer_ID_8842"
    assert record.prior_strategy_frozen is True
    assert not switch.is_strategy_frozen

