"""
Unit Tests for Deterministic Liquidity Sweep Detector (H1).
Verifies lookahead safety, gap-down invalidation, and prior swing low penetration.
"""

import numpy as np
from alphacouncil.alpha.sweep_detector import LiquiditySweepDetector


def test_sweep_detector_requires_minimum_bars():
    detector = LiquiditySweepDetector(lookback=20)
    # Less than 22 bars
    opens = np.ones(15) * 100.0
    highs = np.ones(15) * 105.0
    lows = np.ones(15) * 95.0
    closes = np.ones(15) * 102.0
    vols = np.ones(15) * 1000.0

    sig = detector.evaluate_bar("RELIANCE", opens, highs, lows, closes, vols)
    assert sig is None


def test_sweep_detector_gap_down_invalidation():
    detector = LiquiditySweepDetector(lookback=5)
    # 5 prior bars with swing low at 95.0
    lows = np.array([98.0, 97.0, 95.0, 96.0, 99.0, 90.0])
    highs = np.array([102.0, 101.0, 100.0, 101.0, 103.0, 96.0])
    closes = np.array([100.0, 99.0, 98.0, 100.0, 101.0, 95.5])
    vols = np.array([1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 3000.0])

    # Current bar opens at 94.0 (below prior swing low 95.0) -> Gap-down news crash
    opens = np.array([100.0, 98.0, 97.0, 99.0, 100.0, 94.0])

    sig = detector.evaluate_bar("RELIANCE", opens, highs, lows, closes, vols)
    # Gap-down news crash returns None to avoid truthy falsy bug
    assert sig is None


def test_sweep_detector_valid_bullish_sweep():
    detector = LiquiditySweepDetector(lookback=5, volume_factor=1.5)
    # Prior swing low is 95.0, mean vol is 1000.0
    lows = np.array([98.0, 97.0, 95.0, 96.0, 99.0, 94.0])  # Sweeps to 94.0
    highs = np.array([102.0, 101.0, 100.0, 101.0, 103.0, 97.0])
    closes = np.array([100.0, 99.0, 98.0, 100.0, 101.0, 96.0])  # Rejects and closes above 95.0
    vols = np.array([1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 2200.0])  # 2.2x volume
    opens = np.array([100.0, 98.0, 97.0, 99.0, 100.0, 95.5])  # Opens above 95.0

    sig = detector.evaluate_bar("RELIANCE", opens, highs, lows, closes, vols)
    assert sig is not None
    assert sig.signal == 1
    assert sig.prior_swing_low == 95.0
    assert sig.structural_stop == round(94.0 * 0.9995, 2)
    assert sig.volume_ratio == 2.2
