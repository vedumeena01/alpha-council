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
from alphacouncil.alpha.zone_engine import (
    DemandSupplyEngine,
    CandleType,
    ZoneType,
    MarkingMode,
    TimeframeTier,
)


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


# =====================================================================
# EPISODE 5 TESTS: TRADING PSYCHOLOGY, WICK-TO-WICK & ANTI-NEWS ENGINE
# =====================================================================

def test_episode_05_zone_strength_base_candle_count():
    """
    Episode 5: Zone Strength comparison:
    Setup A (1 base candle) has quick victory -> HIGH_STRENGTH (Score 1.0)
    Setup B (4 base candles) has prolonged struggle -> MODERATE_STRENGTH (Score 0.6)
    """
    engine = DemandSupplyEngine()

    # Setup A: 1 base candle (DBR)
    opens_a = np.array([120.0, 105.0, 107.0])
    highs_a = np.array([121.0, 109.0, 125.0])
    lows_a = np.array([104.0, 101.0, 106.0])
    closes_a = np.array([105.0, 107.0, 124.0])

    z_a = engine.scan_for_zones(opens_a, highs_a, lows_a, closes_a)[0]
    assert z_a.base_candles_count == 1
    assert z_a.strength_rating == "HIGH_STRENGTH"
    assert z_a.strength_score == 1.00

    # Setup B: 4 base candles (DBR)
    # Leg-in (idx 0), Base 1-4 (idx 1..4), Leg-out (idx 5)
    opens_b = np.array([130.0, 105.0, 106.0, 105.5, 106.5, 108.0])
    highs_b = np.array([131.0, 108.0, 107.5, 108.0, 108.5, 136.0])
    lows_b = np.array([104.0, 102.0, 103.0, 102.5, 103.0, 107.0])
    closes_b = np.array([105.0, 106.0, 105.5, 106.5, 107.0, 135.0])

    z_b = engine.scan_for_zones(opens_b, highs_b, lows_b, closes_b)[0]
    assert z_b.base_candles_count == 4
    assert z_b.strength_rating == "MODERATE_STRENGTH"
    assert z_b.strength_score == 0.60


def test_episode_05_wick_to_wick_marking():
    """
    Episode 5: Wick-to-Wick Marking vs Body-to-Wick Marking:
    - Demand:
      Body-to-Wick: PL = max body (107.0)
      Wick-to-Wick: PL = max wick (109.0)
    - Supply:
      Body-to-Wick: PL = min body (113.0)
      Wick-to-Wick: PL = min wick (111.0)
    """
    engine = DemandSupplyEngine()

    # Demand: Base candle Open 105, High 109, Low 101, Close 107
    opens_d = np.array([120.0, 105.0, 107.0])
    highs_d = np.array([121.0, 109.0, 125.0])
    lows_d = np.array([104.0, 101.0, 106.0])
    closes_d = np.array([105.0, 107.0, 124.0])

    z_body = engine.scan_for_zones(
        opens_d, highs_d, lows_d, closes_d, marking_mode=MarkingMode.BODY_TO_WICK
    )[0]
    assert z_body.proximal_line == 107.0  # Max body
    assert z_body.distal_line == 101.0   # Min wick

    z_wick = engine.scan_for_zones(
        opens_d, highs_d, lows_d, closes_d, marking_mode=MarkingMode.WICK_TO_WICK
    )[0]
    assert z_wick.proximal_line == 109.0  # Highest wick!
    assert z_wick.distal_line == 101.0   # Lowest wick
    assert z_wick.marking_mode == MarkingMode.WICK_TO_WICK

    # Supply: Base candle Open 114, High 118, Low 111, Close 113
    opens_s = np.array([100.0, 114.0, 113.0])
    highs_s = np.array([115.0, 118.0, 114.0])
    lows_s = np.array([99.0, 111.0, 98.0])
    closes_s = np.array([114.0, 113.0, 100.0])

    z_s_body = engine.scan_for_zones(
        opens_s, highs_s, lows_s, closes_s, marking_mode=MarkingMode.BODY_TO_WICK
    )[0]
    assert z_s_body.proximal_line == 113.0  # Lowest body
    assert z_s_body.distal_line == 118.0   # Highest wick

    z_s_wick = engine.scan_for_zones(
        opens_s, highs_s, lows_s, closes_s, marking_mode=MarkingMode.WICK_TO_WICK
    )[0]
    assert z_s_wick.proximal_line == 111.0  # Lowest wick!
    assert z_s_wick.distal_line == 118.0   # Highest wick


def test_episode_05_direct_reversal_missing_base_candles():
    """
    Episode 5: Direct Reversals (0 Base Candles):
    Explosive Leg-in immediately followed by explosive Leg-out without basing bar.
    """
    engine = DemandSupplyEngine()

    # V-Reversal Demand: Red drop (Open 120, Close 100) -> Immediate Green rally (Open 100, Close 122)
    opens = np.array([120.0, 100.0])
    highs = np.array([121.0, 125.0])
    lows = np.array([98.0, 96.0])
    closes = np.array([100.0, 122.0])

    zones = engine.scan_for_zones(opens, highs, lows, closes, allow_direct_reversals=True)
    assert len(zones) == 1
    z = zones[0]

    assert z.is_direct_reversal is True
    assert z.base_candles_count == 0
    assert z.strength_rating == "DIRECT_REVERSAL"
    assert z.is_demand is True
    assert z.proximal_line == 100.0  # Interface boundary max(100.0, 100.0)
    assert z.distal_line == 96.0     # min(98.0, 96.0) lowest extreme wick


def test_episode_05_timeframe_hierarchy_dominance():
    """
    Episode 5: Timeframe Hierarchy:
    Monthly (4.0x) >> Weekly (3.0x) >> Daily (2.0x) >> Intraday (1.0x).
    """
    engine = DemandSupplyEngine()
    opens = np.array([120.0, 105.0, 107.0])
    highs = np.array([121.0, 109.0, 125.0])
    lows = np.array([104.0, 101.0, 106.0])
    closes = np.array([105.0, 107.0, 124.0])

    z_monthly = engine.scan_for_zones(
        opens, highs, lows, closes, timeframe=TimeframeTier.MONTHLY
    )[0]
    z_daily = engine.scan_for_zones(
        opens, highs, lows, closes, timeframe=TimeframeTier.DAILY
    )[0]
    z_intraday = engine.scan_for_zones(
        opens, highs, lows, closes, timeframe=TimeframeTier.INTRADAY
    )[0]

    assert z_monthly.timeframe_weight == 4.0
    assert z_daily.timeframe_weight == 2.0
    assert z_intraday.timeframe_weight == 1.0
    assert z_monthly.timeframe_weight > z_daily.timeframe_weight > z_intraday.timeframe_weight


def test_episode_05_psychology_news_trap_evaluation():
    """
    Episode 5 Trading Psychology: "Human can lie, but chart can't."
    - Axis Bank / Nestle Maggi ban case study: Panic news at fresh Demand Zone -> Buy with institutions!
    - HDFC Merger case study: Euphoria news at fresh Supply Zone -> Distribute / Short with institutions!
    """
    engine = DemandSupplyEngine()
    opens = np.array([120.0, 105.0, 107.0])
    highs = np.array([121.0, 109.0, 125.0])
    lows = np.array([104.0, 101.0, 106.0])
    closes = np.array([105.0, 107.0, 124.0])

    z_demand = engine.scan_for_zones(opens, highs, lows, closes)[0]

    # Scenario 1: Media reports accounting scandal / earnings disaster (-0.85 sentiment)
    # Price falls into fresh Demand Zone -> RETAIL_PANIC_LIQUIDITY_TRAP
    trap_d = engine.evaluate_psychology_news_trap(z_demand, news_sentiment_score=-0.85)
    assert trap_d.is_news_trap is True
    assert trap_d.trap_type == "RETAIL_PANIC_LIQUIDITY_TRAP"
    assert trap_d.recommendation == "ACCUMULATE_WITH_INSTITUTIONS"
    assert "Human can lie, but chart can't" in trap_d.rationale

    # Scenario 2: Media reports historic mega-merger / upgrade (+0.90 sentiment)
    # Price rises into fresh Supply Zone -> RETAIL_EUPHORIA_LIQUIDITY_TRAP
    opens_s = np.array([100.0, 114.0, 113.0])
    highs_s = np.array([115.0, 118.0, 114.0])
    lows_s = np.array([99.0, 111.0, 98.0])
    closes_s = np.array([114.0, 113.0, 100.0])

    z_supply = engine.scan_for_zones(opens_s, highs_s, lows_s, closes_s)[0]
    trap_s = engine.evaluate_psychology_news_trap(z_supply, news_sentiment_score=+0.90)
    assert trap_s.is_news_trap is True
    assert trap_s.trap_type == "RETAIL_EUPHORIA_LIQUIDITY_TRAP"
    assert trap_s.recommendation == "DISTRIBUTE_OR_SHORT_WITH_INSTITUTIONS"

    # Scenario 3: Neutral sentiment
    trap_neutral = engine.evaluate_psychology_news_trap(z_demand, news_sentiment_score=0.05)
    assert trap_neutral.is_news_trap is False
    assert trap_neutral.recommendation == "TRADE_STANDARD_PRICE_ACTION"


# =====================================================================
# EPISODE 6 TESTS: PRICE ACTION BEHIND CANDLES (CLOSING, GAP-BASE, GARBAGE)
# =====================================================================

def test_episode_06_closing_concept_demand():
    """
    Episode 6 Concept 1: The Closing Concept in Demand Zones.
    - Proven Zone: Leg-out closes decisively ABOVE Leg-in high.
    - Unproven Zone: Leg-out fails to close above Leg-in high (overhead supply active).
    """
    engine = DemandSupplyEngine()

    # Case A: Proven Zone (Leg-in Drop High = 121.0, Leg-out Rally Close = 124.0 > 121.0)
    opens_a = np.array([120.0, 105.0, 107.0])
    highs_a = np.array([121.0, 109.0, 126.0])
    lows_a = np.array([104.0, 101.0, 106.0])
    closes_a = np.array([105.0, 107.0, 124.0])

    z_proven = engine.scan_for_zones(opens_a, highs_a, lows_a, closes_a)[0]
    assert z_proven.has_clean_closing is True
    assert z_proven.is_proven_zone is True
    assert z_proven.is_high_quality is True

    # Case B: Unproven Zone (Leg-in Drop High = 135.0, Leg-out Rally Close = 118.0 < 135.0)
    opens_b = np.array([130.0, 105.0, 107.0])
    highs_b = np.array([135.0, 109.0, 120.0])  # Leg-in high is 135
    lows_b = np.array([104.0, 101.0, 106.0])
    closes_b = np.array([105.0, 107.0, 118.0])  # Leg-out closes at 118 < 135 (stalled!)

    z_unproven = engine.scan_for_zones(opens_b, highs_b, lows_b, closes_b)[0]
    assert z_unproven.has_clean_closing is False
    assert z_unproven.is_proven_zone is False
    assert z_unproven.is_high_quality is False
    assert z_unproven.strength_score <= 0.60


def test_episode_06_closing_concept_supply():
    """
    Episode 6 Concept 1: The Closing Concept in Supply Zones.
    - Proven Zone: Leg-out closes decisively BELOW Leg-in low.
    - Unproven Zone: Leg-out fails to close below Leg-in low (underlying demand active).
    """
    engine = DemandSupplyEngine()

    # Case A: Proven Zone (Leg-in Rally Low = 99.0, Leg-out Drop Close = 95.0 < 99.0)
    opens_a = np.array([100.0, 114.0, 113.0])
    highs_a = np.array([115.0, 118.0, 114.0])
    lows_a = np.array([99.0, 111.0, 93.0])
    closes_a = np.array([114.0, 113.0, 95.0])

    z_proven = engine.scan_for_zones(opens_a, highs_a, lows_a, closes_a)[0]
    assert z_proven.has_clean_closing is True
    assert z_proven.is_proven_zone is True

    # Case B: Unproven Zone (Leg-in Rally Low = 85.0, Leg-out Drop Close = 100.0 > 85.0)
    opens_b = np.array([90.0, 114.0, 113.0])
    highs_b = np.array([115.0, 118.0, 114.0])
    lows_b = np.array([85.0, 111.0, 98.0])      # Leg-in low is 85
    closes_b = np.array([114.0, 113.0, 100.0])  # Leg-out closes at 100 > 85

    z_unproven = engine.scan_for_zones(opens_b, highs_b, lows_b, closes_b)[0]
    assert z_unproven.has_clean_closing is False
    assert z_unproven.is_proven_zone is False


def test_episode_06_gap_plus_base_equals_exciting_candle():
    """
    Episode 6 Concept 2: Significant Gap + Base Candle = Invisible Exciting Candle.
    - Overnight gap up from 100 to 105.
    - Intraday trades in 104.8 to 105.5 (range 0.7, body 0.2 -> ratio 28% = Base).
    - Synthetic body from 100 is (105.2 - 100) = 5.2 / 5.5 = 94.5% -> Classified GREEN_EXCITING!
    """
    engine = DemandSupplyEngine()
    c = engine.classify_candle(
        index=1,
        open_p=105.0,
        high_p=105.5,
        low_p=104.8,
        close_p=105.2,
        atr14=2.0,
        prev_close=100.0,
        prev_high=100.5,
        prev_low=99.5,
    )
    assert c.candle_type == CandleType.GREEN_EXCITING
    assert c.is_gap_exciting is True
    assert c.gap_distance == 5.0


def test_episode_06_level_on_top_of_level_lotl():
    """
    Episode 6 Concept 2: Stacking Zones (LOTL).
    Zone 2 sits directly above Zone 1 as an absorption cushion.
    """
    engine = DemandSupplyEngine()

    # Zone 1 (Origin Baseline Demand): PL = 100.0, DL = 90.0
    opens = np.array([115.0, 98.0, 100.0, 105.0, 103.0, 104.0])
    highs = np.array([116.0, 102.0, 106.0, 106.5, 105.0, 118.0])
    lows = np.array([97.0, 90.0, 99.0, 102.5, 102.0, 103.5])
    closes = np.array([98.0, 100.0, 105.0, 103.0, 104.0, 117.0])

    zones = engine.scan_for_zones(opens, highs, lows, closes)
    # Detect stacked levels
    lotl = engine.detect_level_on_top_of_level(zones)
    if len(lotl) > 0:
        pair = lotl[0]
        assert pair["type"] == "DEMAND_LOTL"
        assert pair["absorption_cushion_active"] is True
        assert pair["combined_entry"] >= pair["combined_stop_loss"]


def test_episode_06_garbage_area_filtering():
    """
    Episode 6 Concept 5: Garbage Areas.
    Prolonged sideways consolidation of 6+ bars with overlapping wicks and no escape.
    Must be identified and skipped.
    """
    highs = np.array([101.0, 101.2, 100.9, 101.1, 101.0, 101.2, 101.1])
    lows = np.array([100.0, 100.1, 99.8, 100.0, 99.9, 100.1, 100.0])

    is_garbage = DemandSupplyEngine.is_garbage_cluster(highs, lows, start_idx=0, end_idx=6, min_bars=6)
    assert is_garbage is True


def test_episode_06_origin_pivot_isolation():
    """
    Episode 6 Concept 3: Origin of Buying & Selling.
    In a multi-base cluster (>= 3 base candles), locate the true pivot origin candle.
    """
    engine = DemandSupplyEngine()

    # Cluster of 4 base candles (DBR):
    # Base 0: Low 103
    # Base 1: Low 101 (True lowest pivot origin!)
    # Base 2: Low 102
    # Base 3: Low 104
    opens = np.array([125.0, 105.0, 104.0, 103.5, 105.0, 106.0])
    highs = np.array([126.0, 107.0, 106.0, 105.5, 107.0, 122.0])
    lows = np.array([104.0, 103.0, 101.0, 102.0, 104.0, 105.5])
    closes = np.array([105.0, 104.0, 103.5, 105.0, 106.0, 120.0])

    zones = engine.scan_for_zones(opens, highs, lows, closes)
    assert len(zones) == 1
    z = zones[0]
    assert z.base_candles_count == 4
    # Origin candle index must point to index 2 (Base 1, where low was 101.0)
    assert z.origin_candle_idx == 2


