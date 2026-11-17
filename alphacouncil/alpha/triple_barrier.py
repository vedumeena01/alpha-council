"""
Marcos López de Prado Triple Barrier Method & Ornstein-Uhlenbeck Half-Life.
AFML Chapter 3: Path-dependent labeling incorporating profit take, structural stop,
and vertical time barrier.
"""

from dataclasses import dataclass
import numpy as np


@dataclass
class BarrierOutcome:
    """Represents the path-dependent outcome of a Triple Barrier evaluated trade."""
    exit_bar_index: int
    exit_price: float
    barrier_hit: str  # "UPPER", "LOWER", "VERTICAL"
    realized_return_pct: float
    holding_period_days: int
    is_success: bool


class TripleBarrierLabeler:
    """
    Implements Marcos López de Prado's Triple Barrier Method:
    - Upper Barrier: Profit Target (b * D_stop)
    - Lower Barrier: Structural Invalidation Stop
    - Vertical Barrier: Max holding period dynamically bounded by OU half-life
    """

    def __init__(self, payoff_ratio: float = 2.0, max_vertical_days: int = 5):
        self.payoff_ratio = payoff_ratio
        self.max_vertical_days = max_vertical_days

    @staticmethod
    def calculate_ou_half_life(price_series: np.ndarray) -> float:
        """
        Estimates the Ornstein-Uhlenbeck mean-reversion half-life (Dr. Ernest P. Chan).
        Fits: delta_x = alpha + beta * x_{t-1}
        half_life = -ln(2) / beta
        """
        if len(price_series) < 20:
            return 3.0  # Default fallback 3 days

        log_p = np.log(price_series)
        delta_p = np.diff(log_p)
        lag_p = log_p[:-1]

        # Add constant term for OLS
        x = np.column_stack([np.ones_like(lag_p), lag_p])
        try:
            coeffs, _, _, _ = np.linalg.lstsq(x, delta_p, rcond=None)
            beta = coeffs[1]
            if beta < -1e-6:
                half_life = -np.log(2.0) / beta
                return float(np.clip(half_life, 1.0, 10.0))
        except Exception:
            pass
        return 3.0

    def evaluate_path(
        self,
        entry_price: float,
        stop_price: float,
        forward_highs: np.ndarray,
        forward_lows: np.ndarray,
        forward_closes: np.ndarray,
        recent_prices: np.ndarray,
    ) -> BarrierOutcome:
        """
        Evaluates the path-dependent progression of a trade across forward bars.
        """
        d_stop = max(0.01, entry_price - stop_price)
        target_price = entry_price + (self.payoff_ratio * d_stop)

        half_life = self.calculate_ou_half_life(recent_prices)
        effective_vertical_limit = min(self.max_vertical_days, max(3, int(np.ceil(half_life))))

        n_forward = len(forward_closes)
        limit = min(n_forward, effective_vertical_limit)

        for day in range(limit):
            curr_low = forward_lows[day]
            curr_high = forward_highs[day]

            # Conservative check: Lower barrier (Stop) checked before Upper Barrier
            if curr_low <= stop_price:
                ret = (stop_price - entry_price) / entry_price
                return BarrierOutcome(
                    exit_bar_index=day + 1,
                    exit_price=stop_price,
                    barrier_hit="LOWER",
                    realized_return_pct=round(ret, 4),
                    holding_period_days=day + 1,
                    is_success=False,
                )

            if curr_high >= target_price:
                ret = (target_price - entry_price) / entry_price
                return BarrierOutcome(
                    exit_bar_index=day + 1,
                    exit_price=target_price,
                    barrier_hit="UPPER",
                    realized_return_pct=round(ret, 4),
                    holding_period_days=day + 1,
                    is_success=True,
                )

        # Vertical barrier hit (Time limit reached without touching upper/lower)
        final_idx = max(0, limit - 1)
        exit_p = forward_closes[final_idx] if limit > 0 else entry_price
        ret = (exit_p - entry_price) / entry_price

        return BarrierOutcome(
            exit_bar_index=limit,
            exit_price=exit_p,
            barrier_hit="VERTICAL",
            realized_return_pct=round(ret, 4),
            holding_period_days=limit,
            is_success=(ret > 0.0),
        )
