"""
Position Sizing Engine: Exact Units, Volatility Targeting, and BSS-Calibrated Kelly Fraction.
Codifies Section 4A of RFC v5.0 with zero unit mismatch.
"""

from dataclasses import dataclass
from typing import List, Optional
import numpy as np
from alphacouncil.config import PROD_THRESHOLD, HARNESS_KELLY_THRESHOLD

__all__ = ["PositionSizingEngine", "SizingCalculation", "PROD_THRESHOLD", "HARNESS_KELLY_THRESHOLD"]


@dataclass
class SizingCalculation:
    """Detailed position sizing mathematical breakdown."""
    symbol: str
    entry_price: float
    stop_price: float
    stop_distance: float
    atr14: float
    is_noise_trap_skipped: bool
    tau_vol: float
    brier_skill_score: float
    kelly_risk_fraction: float
    tau_effective: float
    shares_quantity: int
    proposed_notional: float
    is_aborted: bool
    regime_mode: str  # "COLD_START", "CALIBRATED_KELLY", "DEFENSIVE", "ABORTED"
    rationale: str


class PositionSizingEngine:
    """
    Computes exact share quantity Q strictly as a function of risk-per-trade fraction.
    """

    def __init__(
        self,
        base_risk_fraction: float = 0.010,  # 1.0% equity risk
        target_annual_vol: float = 0.15,    # 15% target vol
        max_risk_ceiling: float = 0.015,    # 1.5% max risk
        max_notional_pct: float = 0.20,     # 20% max single-stock notional
        min_atr_multiple: float = 0.25,      # Skip if stop < 0.25 * ATR (filters micro-noise without over-discarding sweeps)
        cold_start_trade_threshold: int = HARNESS_KELLY_THRESHOLD, # Minimum closed trades to exit cold start (50 for test harness; 200 for institutional prod)
    ):
        self.base_risk_fraction = base_risk_fraction
        self.target_annual_vol = target_annual_vol
        self.max_risk_ceiling = max_risk_ceiling
        self.max_notional_pct = max_notional_pct
        self.min_atr_multiple = min_atr_multiple
        self.cold_start_trade_threshold = cold_start_trade_threshold

    @staticmethod
    def calculate_brier_skill_score(
        predicted_probs: List[float], outcomes: List[int]
    ) -> float:
        """
        Brier Skill Score (BSS) = 1 - BS / BS_ref.
        Compares probability predictions to sample climatology base-rate.
        """
        n = len(predicted_probs)
        if n < 10:
            return 0.0

        p = np.array(predicted_probs)
        o = np.array(outcomes)

        bs = float(np.mean((p - o) ** 2))
        base_rate = float(np.mean(o))
        bs_ref = float(base_rate * (1.0 - base_rate))

        if bs_ref <= 1e-6:
            return 0.0

        bss = 1.0 - (bs / bs_ref)
        return float(np.clip(bss, -1.0, 1.0))

    def compute_size(
        self,
        symbol: str,
        entry_price: float,
        stop_price: float,
        target_price: float,
        atr14: float,
        realized_annual_vol: float,
        current_equity: float,
        historical_closed_trades_count: int = 0,
        rolling_bss: Optional[float] = None,
        estimated_win_prob: Optional[float] = None,
    ) -> SizingCalculation:
        """
        Computes final share quantity Q according to RFC v5.0 rules.
        Defaults to COLD_START (vol-targeting only) unless sufficient calibrated empirical history exists.
        """
        # 0. Numerical Sanity Check: Fail-Closed on NaN / Inf / Non-positive
        numeric_inputs = [entry_price, stop_price, target_price, atr14, realized_annual_vol, current_equity]
        if not all(np.isfinite(x) for x in numeric_inputs) or atr14 <= 0.0 or current_equity <= 0.0 or entry_price <= 0.0:
            return SizingCalculation(
                symbol=symbol,
                entry_price=entry_price if np.isfinite(entry_price) else 0.0,
                stop_price=stop_price if np.isfinite(stop_price) else 0.0,
                stop_distance=0.0,
                atr14=atr14 if np.isfinite(atr14) else 0.0,
                is_noise_trap_skipped=False,
                tau_vol=0.0,
                brier_skill_score=rolling_bss if (rolling_bss is not None and np.isfinite(rolling_bss)) else 0.0,
                kelly_risk_fraction=0.0,
                tau_effective=0.0,
                shares_quantity=0,
                proposed_notional=0.0,
                is_aborted=True,
                regime_mode="ABORTED",
                rationale="Invalid or non-finite numerical inputs (NaN/Inf or <=0 detected). Fail-closed.",
            )

        stop_distance = max(0.01, entry_price - stop_price)

        # 1. Invalidation Rule (No Artificial Stop Expansion)
        # If stop distance is less than min_atr_multiple * ATR14 (default 0.25 * ATR14 per config.py), skip trade entirely as low-quality noise trap
        if stop_distance < (self.min_atr_multiple * atr14):
            return SizingCalculation(
                symbol=symbol,
                entry_price=entry_price,
                stop_price=stop_price,
                stop_distance=round(stop_distance, 2),
                atr14=round(atr14, 2),
                is_noise_trap_skipped=True,
                tau_vol=0.0,
                brier_skill_score=rolling_bss or 0.0,
                kelly_risk_fraction=0.0,
                tau_effective=0.0,
                shares_quantity=0,
                proposed_notional=0.0,
                is_aborted=True,
                regime_mode="NOISE_TRAP_SKIPPED",
                rationale=f"Stop distance (₹{stop_distance:.2f}) < {self.min_atr_multiple:.1f} * ATR14 (₹{atr14:.2f}). Skipped noise trap.",
            )

        # 2. Volatility-Targeted Base Sizing
        vol_scalar = self.target_annual_vol / max(0.05, realized_annual_vol)
        tau_vol = self.base_risk_fraction * vol_scalar

        # 3. Regime Mode & Effective Risk Selection
        f_star_risk = 0.0
        # Cold start check: Requires at least cold_start_trade_threshold closed trades AND valid BSS AND valid win prob
        if historical_closed_trades_count < self.cold_start_trade_threshold or rolling_bss is None or estimated_win_prob is None:
            regime = "COLD_START"
            tau_eff = min(tau_vol, 0.010)  # Capped at 1.0% in cold start
            msg = f"Cold start (trades={historical_closed_trades_count}<{self.cold_start_trade_threshold} or uncalibrated). Governed strictly by Vol-Targeting (Risk={tau_eff*100:.2f}%)."
        elif rolling_bss <= 0.0:
            regime = "DEFENSIVE"
            tau_eff = min(0.5 * tau_vol, 0.010)  # Defensive risk strictly <= cold-start cap (max 1.0%)
            msg = f"BSS <= 0 ({rolling_bss:.2f}). Probability model uncalibrated. Defensive sizing (Risk={tau_eff*100:.2f}%)."
        else:
            # Calibrated Kelly Calculation
            payoff_b = max(0.1, (target_price - entry_price) / stop_distance)
            p = float(np.clip(estimated_win_prob, 0.05, 0.95))
            edge_expectation = (p * payoff_b) - (1.0 - p)

            if edge_expectation <= 0.0:
                return SizingCalculation(
                    symbol=symbol,
                    entry_price=entry_price,
                    stop_price=stop_price,
                    stop_distance=round(stop_distance, 2),
                    atr14=round(atr14, 2),
                    is_noise_trap_skipped=False,
                    tau_vol=round(tau_vol, 4),
                    brier_skill_score=round(rolling_bss, 4),
                    kelly_risk_fraction=0.0,
                    tau_effective=0.0,
                    shares_quantity=0,
                    proposed_notional=0.0,
                    is_aborted=True,
                    regime_mode="ABORTED",
                    rationale=f"Negative expectancy (Edge={edge_expectation:.3f} <= 0). Trade aborted.",
                )

            raw_kelly = edge_expectation / payoff_b
            f_star_risk = 0.25 * raw_kelly  # Fractional 1/4 Kelly
            regime = "CALIBRATED_KELLY"
            tau_eff = min(tau_vol, f_star_risk)
            msg = f"Calibrated BSS ({rolling_bss:.2f} > 0). Effective Risk min(vol={tau_vol*100:.2f}%, kelly={f_star_risk*100:.2f}%)."

        # Hard Risk Ceiling (One-way valve: can only reduce risk, never boost from below)
        tau_eff = min(tau_eff, self.max_risk_ceiling)
        if tau_eff <= 0.0:
            return SizingCalculation(
                symbol=symbol,
                entry_price=entry_price,
                stop_price=stop_price,
                stop_distance=round(stop_distance, 2),
                atr14=round(atr14, 2),
                is_noise_trap_skipped=False,
                tau_vol=round(tau_vol, 4),
                brier_skill_score=round(rolling_bss or 0.0, 4),
                kelly_risk_fraction=round(f_star_risk, 4),
                tau_effective=0.0,
                shares_quantity=0,
                proposed_notional=0.0,
                is_aborted=True,
                regime_mode="ABORTED",
                rationale="Effective risk calculated non-positive. Trade aborted.",
            )

        # 4. Quantity Calculation & Notional Capping
        raw_quantity = int(np.floor((current_equity * tau_eff) / stop_distance))
        proposed_notional = raw_quantity * entry_price
        max_notional_cap = current_equity * self.max_notional_pct

        final_notional = min(proposed_notional, max_notional_cap)
        final_shares = int(np.floor(final_notional / entry_price))

        return SizingCalculation(
            symbol=symbol,
            entry_price=entry_price,
            stop_price=stop_price,
            stop_distance=round(stop_distance, 2),
            atr14=round(atr14, 2),
            is_noise_trap_skipped=False,
            tau_vol=round(tau_vol, 4),
            brier_skill_score=round(rolling_bss or 0.0, 4),
            kelly_risk_fraction=round(f_star_risk, 4),
            tau_effective=round(tau_eff, 4),
            shares_quantity=final_shares,
            proposed_notional=round(final_shares * entry_price, 2),
            is_aborted=(final_shares <= 0),
            regime_mode=regime,
            rationale=msg,
        )
