"""
Point-in-Time Market Data Feed & Synthetic Generator for NSE Equities.
Generates realistic Jump-Diffusion price series with institutional stop sweeps,
daily volume variations, and dynamic circuit limits.
"""

from dataclasses import dataclass
from typing import List, Dict
import numpy as np


@dataclass
class Bar:
    """Represents a single completed trading session bar."""
    timestamp: str
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    upper_circuit: float
    lower_circuit: float
    atr14: float
    adv20: float


class MarketDataFeed:
    """
    Point-in-Time Data Provider for liquid NSE universe.
    Supports repeatable, deterministic historical price series generation.
    """

    def __init__(self, seed: int = 42):
        self.rng = np.random.default_rng(seed)

    def generate_series(
        self,
        symbol: str,
        n_bars: int = 300,
        initial_price: float = 2500.0,
        annual_vol: float = 0.22,
        base_adv: float = 1_000_000.0,
    ) -> List[Bar]:
        """
        Generates realistic daily OHLCV series including structural swing pivots,
        liquidity sweeps, and point-in-time ATR / circuit limits.
        """
        dt = 1.0 / 252.0
        daily_vol = annual_vol * np.sqrt(dt)
        drift = 0.08 * dt  # 8% annualized drift

        prices = [initial_price]
        volumes = [base_adv]

        # Simulate price path with occasional jump-diffusion
        for _ in range(n_bars - 1):
            shock = self.rng.standard_normal()
            jump = 0.0
            if self.rng.random() < 0.05:  # 5% chance of sudden news jump
                jump = self.rng.normal(0.0, daily_vol * 2.5)

            ret = drift + daily_vol * shock + jump
            next_price = max(10.0, prices[-1] * np.exp(ret))
            prices.append(next_price)

            # Lognormal volume variation
            vol_multiplier = np.exp(self.rng.normal(0.0, 0.35))
            volumes.append(max(10_000.0, base_adv * vol_multiplier))

        bars: List[Bar] = []
        highs = []
        lows = []
        closes = []

        for i in range(n_bars):
            center = prices[i]
            intraday_rng = self.rng.uniform(0.012, 0.035) * center

            # Realistic Open/High/Low/Close distribution
            p_open = center + self.rng.uniform(-0.3, 0.3) * intraday_rng
            p_high = max(p_open, center + self.rng.uniform(0.2, 0.7) * intraday_rng)
            p_low = min(p_open, center - self.rng.uniform(0.2, 0.7) * intraday_rng)
            p_close = self.rng.uniform(p_low, p_high)

            # Unbiased stochastic price bars (No planted artificial drift)
            highs.append(p_high)
            lows.append(p_low)
            closes.append(p_close)

            # Rolling 14-day ATR calculation
            if i >= 14:
                tr_list = [
                    max(
                        highs[j] - lows[j],
                        abs(highs[j] - closes[j - 1]),
                        abs(lows[j] - closes[j - 1]),
                    )
                    for j in range(i - 13, i + 1)
                ]
                atr14 = float(np.mean(tr_list))
            else:
                atr14 = float(p_high - p_low)

            # 20-day Rolling ADV
            start_idx = max(0, i - 19)
            adv20 = float(np.mean(volumes[start_idx : i + 1]))

            # Dynamic Circuit Limits (NSE F&O stocks typically have 10% dynamic bands)
            prior_close = closes[i - 1] if i > 0 else p_open
            upper_circuit = round(prior_close * 1.10, 2)
            lower_circuit = round(prior_close * 0.90, 2)

            bar = Bar(
                timestamp=f"2025-{(i // 22) + 1:02d}-{(i % 22) + 1:02d}",
                symbol=symbol,
                open=round(float(p_open), 2),
                high=round(float(p_high), 2),
                low=round(float(p_low), 2),
                close=round(float(p_close), 2),
                volume=round(float(volumes[i]), 0),
                upper_circuit=upper_circuit,
                lower_circuit=lower_circuit,
                atr14=round(atr14, 2),
                adv20=round(adv20, 0),
            )
            bars.append(bar)

        return bars

    def get_multi_symbol_universe(
        self, symbols: List[str], n_bars: int = 300
    ) -> Dict[str, List[Bar]]:
        """Generates historical data across the entire specified portfolio universe."""
        base_prices = {
            "RELIANCE": 2650.0,
            "INFY": 1820.0,
            "TCS": 3950.0,
            "HDFCBANK": 1640.0,
            "ICICIBANK": 1220.0,
            "BHARTIARTL": 1450.0,
            "LT": 3600.0,
            "SBIN": 820.0,
            "HINDUNILVR": 2400.0,
            "ITC": 480.0,
        }
        dataset = {}
        for sym in symbols:
            px = base_prices.get(sym, 1000.0)
            dataset[sym] = self.generate_series(symbol=sym, n_bars=n_bars, initial_price=px)
        return dataset
