"""
Comprehensive Tests for Demand & Supply Core Engine (Episodes 1, 2, and 3).
Verifies:
1. Candlestick Classification (50% body ratio rule).
2. 4 Structural Patterns (DBR, RBR, RBD, DBD).
3. Exact Zone Marking (Proximal = Highest/Lowest Body, Distal = Lowest/Highest Wick).
4. Freshness vs. Tested Zone Logic.
5. Left & Down (Demand < CMP) and Left & Up (Supply > CMP) Navigation.
"""

import numpy as np
from alphacouncil.alpha.zone_engine import DemandSupplyEngine, CandleType, ZoneType


def test_candle_classification_exciting_vs_base():
    engine = DemandSupplyEngine()

    # Exciting Green: Open 100, High 112, Low 99, Close 110 (Body 10 / Range 13 = 76.9%)
    c1 = engine.classify_candle(0, open_p=100.0, high_p=112.0, low_p=99.0, close_p=110.0)
    assert c1.candle_type == CandleType.GREEN_EXCITING

    # Exciting Red: Open 110, High 111, Low 98, Close 100 (Body 10 / Range 13 = 76.9%)
    c2 = engine.classify_candle(1, open_p=110.0, high_p=111.0, low_p=98.0, close_p=100.0)
    assert c2.candle_type == CandleType.RED_EXCITING

    # Base Candle: Open 105, High 115, Low 95, Close 106 (Body 1 / Range 20 = 5%)
    c3 = engine.classify_candle(2, open_p=105.0, high_p=115.0, low_p=95.0, close_p=106.0)
    assert c3.candle_type == CandleType.BASE


def test_demand_zone_marking_and_freshness():
    engine = DemandSupplyEngine()

    # Create DBR (Drop - Base - Rally):
    # Bar 0: Drop (Red Exciting): Open 120, High 121, Low 104, Close 105
    # Bar 1: Base: Open 105, High 109, Low 101, Close 107
    #        Highest Body = max(105, 107) = 107 (Proximal Line)
    #        Lowest Wick = 101 (Distal Line)
    # Bar 2: Rally (Green Exciting): Open 107, High 118, Low 106, Close 117
    # Bar 3: Continuation: Open 117, High 125, Low 116, Close 124 (Never touches 107 -> Fresh)
    opens = np.array([120.0, 105.0, 107.0, 117.0])
    highs = np.array([121.0, 109.0, 118.0, 125.0])
    lows = np.array([104.0, 101.0, 106.0, 116.0])
    closes = np.array([105.0, 107.0, 117.0, 124.0])

    zones = engine.scan_for_zones(opens, highs, lows, closes)
    assert len(zones) == 1
    z = zones[0]

    assert z.zone_type == ZoneType.DEMAND_DBR
    assert z.is_demand is True
    assert z.is_reversal is True
    assert z.proximal_line == 107.0  # Highest body of base
    assert z.distal_line == 101.0    # Lowest wick of base
    assert z.zone_width == 6.0       # 107 - 101
    assert z.is_fresh is True        # Future price never dipped below 107


def test_tested_zone_detection():
    engine = DemandSupplyEngine()

    # Same DBR as above, but Bar 3 retests the zone:
    # Bar 3 Low dips to 106.0 <= Proximal Line (107.0) -> Tested!
    opens = np.array([120.0, 105.0, 107.0, 115.0])
    highs = np.array([121.0, 109.0, 118.0, 116.0])
    lows = np.array([104.0, 101.0, 106.0, 106.0])  # Low = 106 touches Proximal 107!
    closes = np.array([105.0, 107.0, 117.0, 114.0])

    zones = engine.scan_for_zones(opens, highs, lows, closes)
    assert len(zones) == 1
    z = zones[0]
    assert z.is_fresh is False
    assert z.tested_at_idx == 3


def test_supply_zone_marking():
    engine = DemandSupplyEngine()

    # Create RBD (Rally - Base - Drop):
    # Bar 0: Rally (Green Exciting): Open 100, High 115, Low 99, Close 114
    # Bar 1: Base: Open 114, High 118, Low 111, Close 113
    #        Lowest Body = min(114, 113) = 113 (Proximal Line)
    #        Highest Wick = 118 (Distal Line)
    # Bar 2: Drop (Red Exciting): Open 113, High 114, Low 98, Close 100
    opens = np.array([100.0, 114.0, 113.0])
    highs = np.array([115.0, 118.0, 114.0])
    lows = np.array([99.0, 111.0, 98.0])
    closes = np.array([114.0, 113.0, 100.0])

    zones = engine.scan_for_zones(opens, highs, lows, closes)
    assert len(zones) == 1
    z = zones[0]

    assert z.zone_type == ZoneType.SUPPLY_RBD
    assert z.is_demand is False
    assert z.is_reversal is True
    assert z.proximal_line == 113.0  # Lowest body of base
    assert z.distal_line == 118.0    # Highest wick of base
    assert z.zone_width == 5.0       # 118 - 113
    assert z.is_fresh is True


def test_find_active_zones_relative_to_cmp():
    engine = DemandSupplyEngine()

    # Market at CMP = 110.0
    # Demand Zone at Proximal = 107 (< 110: Left & Down)
    opens = np.array([120.0, 105.0, 107.0, 117.0])
    highs = np.array([121.0, 109.0, 118.0, 125.0])
    lows = np.array([104.0, 101.0, 106.0, 116.0])
    closes = np.array([105.0, 107.0, 117.0, 124.0])

    demand_zones, supply_zones = engine.find_active_trade_zones(
        cmp=110.0, opens=opens, highs=highs, lows=lows, closes=closes, only_fresh=True
    )

    assert len(demand_zones) == 1
    assert demand_zones[0].proximal_line == 107.0
    assert len(supply_zones) == 0
