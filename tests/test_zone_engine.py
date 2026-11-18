"""
Comprehensive Tests for Demand & Supply Core Engine (Episodes 1, 2, 3, and 4).
Verifies:
1. Candlestick Classification (50% body ratio rule).
2. 4 Structural Patterns (DBR, RBR, RBD, DBD).
3. Exact Zone Marking (Proximal = Highest/Lowest Body, Distal = Lowest/Highest Wick).
4. Freshness vs. Tested Zone Logic.
5. Left & Down (Demand < CMP) and Left & Up (Supply > CMP) Navigation.
6. Episode 4: Normal vs. Exceptional Marking (Proximal Line Invariance).
7. Episode 4: Reversal Patterns (DBR/RBD evaluate Leg-in, Base, Leg-out wicks).
8. Episode 4: Continuous Patterns (RBR/DBD evaluate ONLY Base & Leg-out wicks; Leg-in strictly excluded).
9. Episode 4: Trade Execution (Entry slightly above/below PL, SL buffer below/above DL, 2:1 Target).
"""

import numpy as np
from alphacouncil.alpha.zone_engine import DemandSupplyEngine, CandleType, ZoneType


# =====================================================================
# EPISODE 1 TESTS: CHARTING, SESSION PARTITIONS & CANDLE MECHANICS
# =====================================================================

def test_episode_01_nse_session_partitions_no_orphan_candles():
    """
    Episode 1: 375-minute Indian session partition:
    75m bars = 5 per day, 125m bars = 3 per day.
    """
    parts = DemandSupplyEngine.get_nse_session_partitions()
    assert parts["session_minutes"] == 375
    assert parts["75m_bars"] == 5
    assert parts["125m_bars"] == 3
    assert (parts["session_minutes"] % 75) == 0
    assert (parts["session_minutes"] % 125) == 0


def test_episode_01_wickless_candles_directional_power():
    """
    Episode 1: Pure directional candles without wicks:
    - Open == Low -> Pure green buying pressure
    - Open == High -> Pure red selling pressure
    """
    is_w, label = DemandSupplyEngine.is_wickless_candle(100.0, 115.0, 100.0, 114.0)
    assert is_w is True
    assert label == "OPEN_EQUALS_LOW_PURE_BUYING"

    is_w, label = DemandSupplyEngine.is_wickless_candle(150.0, 150.0, 130.0, 132.0)
    assert is_w is True
    assert label == "OPEN_EQUALS_HIGH_PURE_SELLING"

    is_w, label = DemandSupplyEngine.is_wickless_candle(100.0, 115.0, 95.0, 110.0)
    assert is_w is False
    assert label == "STANDARD_CANDLE"


# =====================================================================
# EPISODE 2 TESTS: 50% BODY RATIO RULE & CANDLE CLASSIFICATION
# =====================================================================

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


# =====================================================================
# EPISODE 3 TESTS: ZONE MARKING, PROXIMAL/DISTAL LINES & FRESHNESS
# =====================================================================

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


# =====================================================================
# EPISODE 4 TESTS: EXCEPTIONAL MARKING & EXECUTION LEVELS
# =====================================================================

def test_exceptional_marking_dbr_vedanta_case_study():
    """
    Vedanta Case Study: Leg-in has an extended lower wick below base candle wicks.
    Under Normal Marking: DL = Base Low (triggers premature stopout during market sell-off).
    Under Exceptional Marking: DL = Leg-in Low (protects position from the speeding bus).
    Proximal Line remains strictly invariant.
    """
    engine = DemandSupplyEngine(use_exceptional_marking=True)

    # Bar 0: Leg-in Drop: Open 250, High 251, Low 190, Close 200 (Long lower wick down to 190)
    # Bar 1: Base: Open 200, High 205, Low 198, Close 203 (Base low is 198, Highest body is 203)
    # Bar 2: Leg-out Rally: Open 203, High 230, Low 202, Close 228
    opens = np.array([250.0, 200.0, 203.0])
    highs = np.array([251.0, 205.0, 230.0])
    lows = np.array([190.0, 198.0, 202.0])
    closes = np.array([200.0, 203.0, 228.0])

    # Scan with exceptional marking (default)
    zones = engine.scan_for_zones(opens, highs, lows, closes)
    assert len(zones) == 1
    z = zones[0]

    assert z.zone_type == ZoneType.DEMAND_DBR
    assert z.proximal_line == 203.0  # Highest body of base (Invariant!)
    assert z.distal_line_normal == 198.0  # Base wick only
    assert z.distal_line_exceptional == 190.0  # Extended leg-in wick
    assert z.distal_line == 190.0  # Active DL is exceptional
    assert z.zone_width == 13.0  # 203 - 190

    # Test that normal mode keeps distal at 198
    zones_normal = engine.scan_for_zones(opens, highs, lows, closes, use_exceptional=False)
    assert zones_normal[0].distal_line == 198.0
    assert zones_normal[0].proximal_line == 203.0  # Proximal Invariance confirmed


def test_exceptional_marking_dbr_alkyl_amines_case_study():
    """
    Alkyl Amines Case Study: Dual wick exception.
    Both leg-in and leg-out dip below the base candle, but leg-out is lowest.
    DL = min(Leg-in low, Base low, Leg-out low).
    """
    engine = DemandSupplyEngine(use_exceptional_marking=True)

    # Bar 0: Leg-in Drop: Open 300, High 301, Low 255, Close 260
    # Bar 1: Base: Open 260, High 265, Low 258, Close 262
    # Bar 2: Leg-out Rally: Open 262, High 290, Low 250, Close 288 (Extreme dip to 250)
    opens = np.array([300.0, 260.0, 262.0])
    highs = np.array([301.0, 265.0, 290.0])
    lows = np.array([255.0, 258.0, 250.0])
    closes = np.array([260.0, 262.0, 288.0])

    zones = engine.scan_for_zones(opens, highs, lows, closes)
    assert len(zones) == 1
    z = zones[0]

    assert z.proximal_line == 262.0
    assert z.distal_line_normal == 258.0
    assert z.distal_line_exceptional == 250.0  # Leg-out wick was the extreme
    assert z.distal_line == 250.0


def test_exceptional_marking_rbr_continuous_strictly_ignores_leg_in():
    """
    Continuous Pattern Rule: In RBR and DBD, Leg-in is STRICTLY EXCLUDED.
    Leg-in belonged to an independent prior trend and was not part of basing struggle.
    DL evaluates ONLY [Base, Leg-out].
    """
    engine = DemandSupplyEngine(use_exceptional_marking=True)

    # Bar 0: Leg-in Rally: Open 100, High 130, Low 85, Close 128 (Extreme low wick at 85)
    # Bar 1: Base: Open 128, High 132, Low 125, Close 130
    # Bar 2: Leg-out Rally: Open 130, High 150, Low 127, Close 148
    opens = np.array([100.0, 128.0, 130.0])
    highs = np.array([130.0, 132.0, 150.0])
    lows = np.array([85.0, 125.0, 127.0])
    closes = np.array([128.0, 130.0, 148.0])

    zones = engine.scan_for_zones(opens, highs, lows, closes)
    assert len(zones) == 1
    z = zones[0]

    assert z.zone_type == ZoneType.DEMAND_RBR
    assert z.is_reversal is False
    assert z.proximal_line == 130.0
    assert z.distal_line_normal == 125.0
    # Leg-in low (85.0) MUST BE IGNORED!
    assert z.distal_line_exceptional == 125.0
    assert z.distal_line == 125.0


def test_exceptional_marking_continuous_rbr_with_leg_out_wick():
    """
    RBR where Leg-out dips lower than the base candle wicks.
    DL shifts to the leg-out wick.
    """
    engine = DemandSupplyEngine(use_exceptional_marking=True)

    # Bar 0: Leg-in Rally: Open 100, High 130, Low 98, Close 128
    # Bar 1: Base: Open 128, High 132, Low 125, Close 130
    # Bar 2: Leg-out Rally: Open 130, High 150, Low 122, Close 148 (Dips to 122 < 125)
    opens = np.array([100.0, 128.0, 130.0])
    highs = np.array([130.0, 132.0, 150.0])
    lows = np.array([98.0, 125.0, 122.0])
    closes = np.array([128.0, 130.0, 148.0])

    zones = engine.scan_for_zones(opens, highs, lows, closes)
    z = zones[0]

    assert z.distal_line_normal == 125.0
    assert z.distal_line_exceptional == 122.0  # Leg-out wick taken
    assert z.distal_line == 122.0


def test_exceptional_marking_supply_patterns():
    """
    Supply Reversal (RBD): Evaluates Leg-in, Base, Leg-out highest wicks.
    Supply Continuous (DBD): Evaluates ONLY Base and Leg-out (ignores Leg-in).
    """
    engine = DemandSupplyEngine(use_exceptional_marking=True)

    # RBD (Reversal): Leg-in has highest upper wick at 155
    opens = np.array([110.0, 144.0, 142.0])
    highs = np.array([155.0, 145.0, 143.0])  # Leg-in peak 155
    lows = np.array([109.0, 140.0, 120.0])
    closes = np.array([144.0, 142.0, 122.0])

    z_rbd = engine.scan_for_zones(opens, highs, lows, closes)[0]
    assert z_rbd.zone_type == ZoneType.SUPPLY_RBD
    assert z_rbd.proximal_line == 142.0  # Lowest body of base
    assert z_rbd.distal_line_normal == 145.0  # Base wick
    assert z_rbd.distal_line_exceptional == 155.0  # Leg-in upper wick
    assert z_rbd.distal_line == 155.0

    # DBD (Continuous): Leg-in has peak at 200 from previous drop (must be IGNORED)
    opens_dbd = np.array([190.0, 144.0, 142.0])
    highs_dbd = np.array([200.0, 145.0, 148.0])  # Leg-out peak 148 > Base 145
    lows_dbd = np.array([145.0, 140.0, 120.0])
    closes_dbd = np.array([145.0, 142.0, 122.0])

    z_dbd = engine.scan_for_zones(opens_dbd, highs_dbd, lows_dbd, closes_dbd)[0]
    assert z_dbd.zone_type == ZoneType.SUPPLY_DBD
    assert z_dbd.proximal_line == 142.0
    assert z_dbd.distal_line_normal == 145.0
    # Leg-in (200) ignored, Leg-out (148) evaluated
    assert z_dbd.distal_line_exceptional == 148.0
    assert z_dbd.distal_line == 148.0


def test_execution_orders_entry_sl_target_calculations():
    """
    Verifies Episode 4 Execution Rules:
    1. Demand: Entry = PL + buffer, SL = DL - buffer, Target = Entry + 2*Risk (2:1 RRR)
    2. Supply: Entry = PL - buffer, SL = DL + buffer, Target = Entry - 2*Risk (2:1 RRR)
    """
    # 5% buffer ratio for clear arithmetic testing
    engine = DemandSupplyEngine(buffer_ratio=0.05, target_rrr=2.0)

    # Demand Setup (DBR):
    # Proximal = 200.0, Distal = 190.0 -> Zone width = 10.0
    # Buffer = 10.0 * 0.05 = 0.50
    # Entry = 200.0 + 0.50 = 200.50
    # SL = 190.0 - 0.50 = 189.50
    # Risk = 200.50 - 189.50 = 11.00
    # Target (2:1) = 200.50 + (2 * 11.00) = 222.50
    # Reward = 22.00
    opens = np.array([230.0, 195.0, 200.0])
    highs = np.array([231.0, 202.0, 225.0])
    lows = np.array([195.0, 190.0, 198.0])
    closes = np.array([195.0, 200.0, 224.0])

    z_demand = engine.scan_for_zones(opens, highs, lows, closes)[0]
    assert z_demand.proximal_line == 200.0
    assert z_demand.distal_line == 190.0
    assert z_demand.zone_width == 10.0

    assert z_demand.entry_price == 200.50
    assert z_demand.stop_loss == 189.50
    assert z_demand.risk_per_share == 11.00
    assert z_demand.target_price == 222.50
    assert z_demand.reward_per_share == 22.00
    assert z_demand.risk_reward_ratio == 2.0

    # Supply Setup (RBD):
    # Base open 150, close 145 (Lowest body = 145 = PL)
    # Base high 155 (Highest wick = 155 = DL)
    # Zone width = 155 - 145 = 10.0
    # Buffer = 10.0 * 0.05 = 0.50
    # Entry = 145.0 - 0.50 = 144.50 (slightly below PL)
    # SL = 155.0 + 0.50 = 155.50 (slightly above DL)
    # Risk = 155.50 - 144.50 = 11.00
    # Target (2:1) = 144.50 - (2 * 11.00) = 122.50
    # Reward = 22.00
    opens_s = np.array([120.0, 150.0, 145.0])
    highs_s = np.array([146.0, 155.0, 145.0])
    lows_s = np.array([119.0, 144.0, 120.0])
    closes_s = np.array([145.0, 145.0, 122.0])

    z_supply = engine.scan_for_zones(opens_s, highs_s, lows_s, closes_s)[0]
    assert z_supply.proximal_line == 145.0
    assert z_supply.distal_line == 155.0
    assert z_supply.zone_width == 10.0

    assert z_supply.entry_price == 144.50
    assert z_supply.stop_loss == 155.50
    assert z_supply.risk_per_share == 11.00
    assert z_supply.target_price == 122.50
    assert z_supply.reward_per_share == 22.00
    assert z_supply.risk_reward_ratio == 2.0
