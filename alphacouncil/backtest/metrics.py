"""
Institutional Quantitative Performance Metrics & Marcos López de Prado Deflated Sharpe Ratio (DSR).
AFML Chapter 14: Adjusts Sharpe Ratio for selection bias (N_trials) and non-Gaussian skew/kurtosis.
"""

from dataclasses import dataclass
from typing import List
import numpy as np
# Pure numpy implementation for maximum portability and deterministic execution


@dataclass
class PerformanceMetrics:
    """Institutional portfolio performance summary."""
    total_return_pct: float
    annualized_return_pct: float
    annualized_volatility_pct: float
    sharpe_ratio: float
    deflated_sharpe_ratio: float  # DSR (López de Prado)
    sortino_ratio: float
    max_drawdown_pct: float
    calmar_ratio: float
    win_rate_pct: float
    profit_factor: float
    total_trades: int
    trials_logged: int


class QuantMetricsCalculator:
    """
    Computes rigorous performance metrics and DSR.
    """

    @staticmethod
    def _norm_cdf(x: float) -> float:
        """Approximation of Standard Normal Cumulative Distribution Function (error < 7.5e-8)."""
        # Abramowitz and Stegun approximation
        b0 = 0.2316419
        b1 = 0.319381530
        b2 = -0.356563782
        b3 = 1.781477937
        b4 = -1.821255978
        b5 = 1.330274429

        if x >= 0.0:
            t = 1.0 / (1.0 + b0 * x)
            poly = t * (b1 + t * (b2 + t * (b3 + t * (b4 + t * b5))))
            phi = (1.0 / np.sqrt(2.0 * np.pi)) * np.exp(-0.5 * x * x)
            return float(1.0 - phi * poly)
        else:
            return float(1.0 - QuantMetricsCalculator._norm_cdf(-x))

    @staticmethod
    def compute_deflated_sharpe_ratio(
        returns: np.ndarray,
        n_trials: int = 150,
        benchmark_sr: float = 0.0,
    ) -> float:
        """
        Marcos López de Prado Deflated Sharpe Ratio (AFML Chapter 14).
        Adjusts for multiple testing selection bias and non-normality (skewness, kurtosis).
        """
        n = len(returns)
        if n < 30:
            return 0.50

        mean_r = float(np.mean(returns))
        std_r = float(np.std(returns, ddof=1))
        if std_r < 1e-8:
            return 0.0

        daily_sr = mean_r / std_r

        # Higher statistical moments
        z = (returns - mean_r) / std_r
        skew = float(np.mean(z ** 3))
        kurt = float(np.mean(z ** 4))  # Pearson kurtosis (Normal = 3)

        # Expected maximum annualized Sharpe under Null Hypothesis of zero skill across N_trials
        # Bailey & López de Prado (2014) / AFML Chapter 14
        gamma_em = 0.5772156649
        if n_trials > 1:
            log_n = np.log(n_trials)
            sr_star_ann = np.sqrt(2.0 * log_n) + (gamma_em / np.sqrt(2.0 * log_n))
            # Convert annualized expected max to daily scale
            sr_star = sr_star_ann / np.sqrt(252.0)
        else:
            sr_star = benchmark_sr / np.sqrt(252.0)

        # Variance of the Sharpe ratio estimator (Mertens 2002)
        var_sr = (1.0 - (skew * daily_sr) + (((kurt - 1.0) / 4.0) * (daily_sr ** 2))) / (n - 1)

        if var_sr <= 1e-8:
            return 0.50

        # DSR Z-score: Probability that true Sharpe exceeds expected maximum from multiple testing
        z_stat = (daily_sr - sr_star) / np.sqrt(var_sr)
        dsr_prob = QuantMetricsCalculator._norm_cdf(z_stat)

        return float(np.clip(dsr_prob, 0.001, 0.999))

    @staticmethod
    def compute_performance(
        daily_equity_curve: List[float],
        trade_pnls: List[float],
        n_trials_logged: int = 150,
        risk_free_rate: float = 0.0,
    ) -> PerformanceMetrics:
        """
        Computes comprehensive institutional metrics.
        risk_free_rate: Annualized risk-free benchmark (default 0.0 for pure excess returns).
        """
        eq = np.array(daily_equity_curve)
        n_days = len(eq)
        if n_days < 2:
            return PerformanceMetrics(
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, n_trials_logged
            )

        daily_returns = np.diff(eq) / eq[:-1]

        total_ret = (eq[-1] - eq[0]) / eq[0]
        ann_ret = (1.0 + total_ret) ** (252.0 / max(1, n_days)) - 1.0

        daily_vol = float(np.std(daily_returns, ddof=1)) if len(daily_returns) > 1 else 0.0
        ann_vol = daily_vol * np.sqrt(252.0)

        # Excess return over risk-free rate
        rf_daily = (1.0 + risk_free_rate) ** (1.0 / 252.0) - 1.0
        excess_daily_returns = daily_returns - rf_daily
        daily_excess_mean = float(np.mean(excess_daily_returns))
        sharpe = (daily_excess_mean / (daily_vol + 1e-8)) * np.sqrt(252.0)

        # Downside volatility for Sortino
        neg_returns = daily_returns[daily_returns < 0.0]
        downside_vol = (
            float(np.std(neg_returns, ddof=1)) * np.sqrt(252.0)
            if len(neg_returns) > 1
            else ann_vol
        )
        sortino = ann_ret / (downside_vol + 1e-8)

        # Max Drawdown
        peaks = np.maximum.accumulate(eq)
        drawdowns = (peaks - eq) / peaks
        max_dd = float(np.max(drawdowns)) if len(drawdowns) > 0 else 0.0

        calmar = ann_ret / (max_dd + 1e-8)

        # Trade metrics
        n_trades = len(trade_pnls)
        if n_trades > 0:
            wins = [p for p in trade_pnls if p > 0.0]
            losses = [p for p in trade_pnls if p < 0.0]
            win_rate = len(wins) / n_trades
            profit_factor = (
                sum(wins) / (abs(sum(losses)) + 1e-8) if losses else 99.0
            )
        else:
            win_rate = 0.0
            profit_factor = 0.0

        dsr = QuantMetricsCalculator.compute_deflated_sharpe_ratio(
            daily_returns, n_trials=n_trials_logged
        )

        return PerformanceMetrics(
            total_return_pct=round(total_ret * 100, 2),
            annualized_return_pct=round(ann_ret * 100, 2),
            annualized_volatility_pct=round(ann_vol * 100, 2),
            sharpe_ratio=round(sharpe, 2),
            deflated_sharpe_ratio=round(dsr, 3),
            sortino_ratio=round(sortino, 2),
            max_drawdown_pct=round(max_dd * 100, 2),
            calmar_ratio=round(calmar, 2),
            win_rate_pct=round(win_rate * 100, 1),
            profit_factor=round(profit_factor, 2),
            total_trades=n_trades,
            trials_logged=n_trials_logged,
        )
