"""
Deterministic Structural Liquidity Sweep Detector (Hypothesis H1).
Vectorized, lookahead-free algorithm operating on completed daily bars.
Execution executes strictly on next-bar open (t+1 Open).
"""

from dataclasses import dataclass
from typing import Optional, List
import numpy as np


@dataclass
class SweepSignal:
    """Detailed structural liquidity sweep signal output."""
    symbol: str
    bar_index: int
    signal: int  # +1 for Bullish Reversal, 0 for None
    prior_swing_low: float
    trigger_bar_close: float
    structural_stop: float
    volume_ratio: float
    reason: str


class LiquiditySweepDetector:
    """
    Implements Hypothesis H1 (Structural Sell-Side Liquidity Sweep).
    Microstructure: Retail sell-stop cascades below support absorbed by institutional buyers.
    """

    def __init__(self, lookback: int = 20, volume_factor: float = 1.5):
        self.lookback = lookback
        self.volume_factor = volume_factor

    def evaluate_bar(
        self,
        symbol: str,
        open_p: np.ndarray,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        volume: np.ndarray,
        bar_idx: int = -1,
    ) -> Optional[SweepSignal]:
        """
        Evaluates the setup at the close of completed Bar t.
        Execution is scheduled for Bar t+1 Open.
        """
        n = len(close)
        if n < self.lookback + 1:
            return None

        # Prior reference window: [t - lookback - 1, t - 1] (strictly excludes current bar t)
        prior_window_lows = low[-self.lookback - 1 : -1]
        prior_window_vols = volume[-self.lookback - 1 : -1]

        prior_swing_low = float(np.min(prior_window_lows))
        vol_sma = float(np.mean(prior_window_vols))

        curr_open = float(open_p[-1])
        curr_low = float(low[-1])
        curr_close = float(close[-1])
        curr_vol = float(volume[-1])

        vol_ratio = curr_vol / (vol_sma + 1e-8)

        # Filter 1: Overnight Gap-Down Invalidation
        # If open is already below prior swing low, move is news-driven overnight gap, not stop run
        if curr_open < prior_swing_low:
            return None

        # Filter 2: Volume Sanity (Require non-zero historical volume)
        if vol_sma <= 0.0 or curr_vol <= 0.0:
            return None

        # Condition: Sell-Side Liquidity Swept -> Bullish Institutional Reversal
        is_sweep = (curr_low < prior_swing_low) and (curr_close > prior_swing_low)
        is_vol_confirmed = curr_vol >= (self.volume_factor * vol_sma)

        if is_sweep and is_vol_confirmed:
            actual_bar_idx = (n - 1) if bar_idx == -1 else bar_idx
            structural_stop = round(curr_low * 0.9995, 2)  # Low_t - 0.05%
            return SweepSignal(
                symbol=symbol,
                bar_index=actual_bar_idx,
                signal=1,
                prior_swing_low=round(prior_swing_low, 2),
                trigger_bar_close=round(curr_close, 2),
                structural_stop=structural_stop,
                volume_ratio=round(vol_ratio, 2),
                reason="Confirmed: Retail stop sweep absorbed with 1.5x+ volume expansion",
            )

        return None

    def scan_series(
        self,
        symbol: str,
        open_p: np.ndarray,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        volume: np.ndarray,
    ) -> List[SweepSignal]:
        """Scans a historical series and returns all generated sweep signals."""
        signals = []
        n = len(close)
        for i in range(self.lookback + 2, n + 1):
            sig = self.evaluate_bar(
                symbol=symbol,
                open_p=open_p[:i],
                high=high[:i],
                low=low[:i],
                close=close[:i],
                volume=volume[:i],
                bar_idx=i - 1,
            )
            if sig and sig.signal == 1:
                signals.append(sig)
        return signals
