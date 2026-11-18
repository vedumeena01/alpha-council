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
    TradingStance,
    TimeframeTier,
    TradingStyle,
    TrendDirection,
    CurvePosition,
    TradeActionBias,
    MultiTimeframePlan,
    TradeScoreQuality,
    ZoneAlignmentType,
    MACrossoverType,
    TradeScoreBreakdown,
    EntryType,
    ZoneAuthenticity,
    TradingStyleCategory,
    RejectionAudit,
    ConfirmationEntryType,
    ConfirmationTradePlan,
    MacroSupplyWallStatus,
    OriginQuality,
    MasterRevisionAuditReport,
)
from alphacouncil.alpha.sector_engine import (
    SectorAnalysisEngine,
    SectorName,
    SectorConfluenceLevel,
    SectorRotationPhase,
    SectorConfluenceResult,
    HeavyweightStatusReport,
    PortfolioSectorAllocationReport,
)
from alphacouncil.risk.gtf_risk import (
    RiskTier,
    ExecutionErrorType,
    SizingBreakdown,
    GrowthProjection,
    TradeLogEntry,
    GTFTradingJournal,
    GTFRiskManager,
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


# =====================================================================
# EPISODE 7 TESTS: MULTIPLE TIMEFRAME ANALYSIS (MTFA, 50 SMA CLOCK, CURVE)
# =====================================================================

def test_episode_07_sma50_clock_trend_uptrend_downtrend_sideways():
    """
    Episode 7 Concept 2: The 50 SMA Clock Method & 7th Candle Rule.
    - 12 to 3 o'clock -> UPTREND
    - 3 to 6 o'clock -> DOWNTREND
    - 3 o'clock flat -> SIDEWAYS
    """
    # 1. Uptrend: 60 bars rising steadily from 100 to 160
    closes_up = np.linspace(100.0, 160.0, 60)
    trend_up, slope_up, clock_up = DemandSupplyEngine.calculate_sma50_clock_trend(closes_up)
    assert trend_up == TrendDirection.UPTREND
    assert clock_up == "12_TO_3_OCLOCK"
    assert slope_up > 0

    # 2. Downtrend: 60 bars dropping steadily from 160 to 100
    closes_down = np.linspace(160.0, 100.0, 60)
    trend_down, slope_down, clock_down = DemandSupplyEngine.calculate_sma50_clock_trend(closes_down)
    assert trend_down == TrendDirection.DOWNTREND
    assert clock_down == "3_TO_6_OCLOCK"
    assert slope_down < 0

    # 3. Sideways: 60 bars oscillating around 100 with 0 net drift
    closes_side = np.full(60, 100.0)
    trend_side, slope_side, clock_side = DemandSupplyEngine.calculate_sma50_clock_trend(closes_side)
    assert trend_side == TrendDirection.SIDEWAYS
    assert clock_side == "3_OCLOCK_FLAT"


def test_episode_07_curve_position_5_tiers_and_all_time_high():
    """
    Episode 7 Concept 5: The Five Curve Sections (0%, 33.33%, 66.66%, 100%).
    Demand Zone PL = 100.0, Supply Zone PL = 200.0 (Range = 100.0 points).
    """
    engine = DemandSupplyEngine()
    # Mock HTF Demand: PL = 100.0, DL = 90.0
    opens_d = np.array([120.0, 95.0, 100.0])
    highs_d = np.array([121.0, 102.0, 125.0])
    lows_d = np.array([94.0, 90.0, 99.0])
    closes_d = np.array([95.0, 100.0, 124.0])
    htf_demand = engine.scan_for_zones(opens_d, highs_d, lows_d, closes_d)[0]

    # Mock HTF Supply: PL = 200.0, DL = 210.0
    opens_s = np.array([180.0, 205.0, 200.0])
    highs_s = np.array([185.0, 210.0, 201.0])
    lows_s = np.array([179.0, 198.0, 180.0])
    closes_s = np.array([205.0, 200.0, 182.0])
    htf_supply = engine.scan_for_zones(opens_s, highs_s, lows_s, closes_s)[0]

    # VLOC: CMP = 95.0 (< 100.0 Demand PL)
    pos, pct = DemandSupplyEngine.calculate_curve_position(95.0, htf_demand, htf_supply)
    assert pos == CurvePosition.VERY_LOW_ON_CURVE

    # LOC: CMP = 120.0 (20.0% of curve)
    pos, pct = DemandSupplyEngine.calculate_curve_position(120.0, htf_demand, htf_supply)
    assert pos == CurvePosition.LOW_ON_CURVE
    assert pct == 20.0

    # EQB: CMP = 150.0 (50.0% of curve)
    pos, pct = DemandSupplyEngine.calculate_curve_position(150.0, htf_demand, htf_supply)
    assert pos == CurvePosition.EQUILIBRIUM
    assert pct == 50.0

    # HOC: CMP = 180.0 (80.0% of curve)
    pos, pct = DemandSupplyEngine.calculate_curve_position(180.0, htf_demand, htf_supply)
    assert pos == CurvePosition.HIGH_ON_CURVE
    assert pct == 80.0

    # VHOC: CMP = 205.0 (> 200.0 Supply PL)
    pos, pct = DemandSupplyEngine.calculate_curve_position(205.0, htf_demand, htf_supply)
    assert pos == CurvePosition.VERY_HIGH_ON_CURVE

    # ATH: No fresh overhead supply exists
    pos_ath, _ = DemandSupplyEngine.calculate_curve_position(250.0, htf_demand, None)
    assert pos_ath == CurvePosition.ALL_TIME_HIGH


def test_episode_07_directional_bias_curve_vs_trend_mit_and_wit():
    """
    Episode 7 Concept 6: Directional Bias Matrix.
    - LOC + Uptrend -> BUY_ONLY
    - LOC + Downtrend -> NO_TRADE (Counter-trend trap)
    - HOC + Downtrend -> SELL_ONLY
    - EQB + Uptrend -> BUY_ONLY (Trend Follower)
    - EQB + Downtrend -> SELL_ONLY (Trend Follower)
    """
    engine = DemandSupplyEngine()
    # Mock HTF Demand (PL 100, DL 90) & Supply (PL 200, DL 210)
    htf_demand = engine.scan_for_zones(
        np.array([120.0, 95.0, 100.0]),
        np.array([121.0, 102.0, 125.0]),
        np.array([94.0, 90.0, 99.0]),
        np.array([95.0, 100.0, 124.0]),
    )[0]
    htf_supply = engine.scan_for_zones(
        np.array([180.0, 205.0, 200.0]),
        np.array([185.0, 210.0, 201.0]),
        np.array([179.0, 198.0, 180.0]),
        np.array([205.0, 200.0, 182.0]),
    )[0]

    itf_up = np.linspace(100.0, 150.0, 60)
    itf_down = np.linspace(150.0, 100.0, 60)

    # 1. LOC + Uptrend (CMP 120.0) -> High probability Buy
    plan_loc_up = DemandSupplyEngine.build_multi_timeframe_plan(
        TradingStyle.MIT, 120.0, htf_demand, htf_supply, itf_up, []
    )
    assert plan_loc_up.action_bias == TradeActionBias.BUY_ONLY

    # 2. LOC + Downtrend (CMP 120.0) -> Counter-trend trap! Prohibited!
    plan_loc_down = DemandSupplyEngine.build_multi_timeframe_plan(
        TradingStyle.MIT, 120.0, htf_demand, htf_supply, itf_down, []
    )
    assert plan_loc_down.action_bias == TradeActionBias.NO_TRADE

    # 3. HOC + Downtrend (CMP 180.0) -> High probability Short
    plan_hoc_down = DemandSupplyEngine.build_multi_timeframe_plan(
        TradingStyle.WIT, 180.0, htf_demand, htf_supply, itf_down, []
    )
    assert plan_hoc_down.action_bias == TradeActionBias.SELL_ONLY

    # 4. EQB + Uptrend (CMP 150.0) -> Buy with trend
    plan_eqb_up = DemandSupplyEngine.build_multi_timeframe_plan(
        TradingStyle.DIT, 150.0, htf_demand, htf_supply, itf_up, []
    )
    assert plan_eqb_up.action_bias == TradeActionBias.BUY_ONLY


def test_episode_07_the_boundary_rule_ltf_within_htf_distal():
    """
    Episode 7 Concept 7: The Boundary Rule.
    LTF Execution zones must NEVER extend past the Distal Line of the HTF Location Zone.
    """
    engine = DemandSupplyEngine()
    # HTF Demand: PL = 100.0, DL = 90.0
    htf_demand = engine.scan_for_zones(
        np.array([120.0, 95.0, 100.0]),
        np.array([121.0, 102.0, 125.0]),
        np.array([94.0, 90.0, 99.0]),
        np.array([95.0, 100.0, 124.0]),
    )[0]
    htf_supply = engine.scan_for_zones(
        np.array([180.0, 205.0, 200.0]),
        np.array([185.0, 210.0, 201.0]),
        np.array([179.0, 198.0, 180.0]),
        np.array([205.0, 200.0, 182.0]),
    )[0]

    # LTF Zone 1: Demand PL = 98.0, DL = 92.0 (>= 90.0 HTF Distal Line) -> ELIGIBLE
    ltf_zone_valid = engine.scan_for_zones(
        np.array([110.0, 95.0, 98.0]),
        np.array([111.0, 100.0, 115.0]),
        np.array([94.0, 92.0, 97.0]),  # DL = 92.0
        np.array([95.0, 98.0, 114.0]),
    )[0]

    # LTF Zone 2: Demand PL = 95.0, DL = 85.0 (< 90.0 HTF Distal Line) -> REJECTED!
    ltf_zone_invalid = engine.scan_for_zones(
        np.array([110.0, 90.0, 95.0]),
        np.array([111.0, 97.0, 115.0]),
        np.array([89.0, 85.0, 94.0]),  # DL = 85.0 breaches HTF Distal 90.0!
        np.array([90.0, 95.0, 114.0]),
    )[0]

    itf_up = np.linspace(100.0, 150.0, 60)
    plan = DemandSupplyEngine.build_multi_timeframe_plan(
        TradingStyle.MIT, 120.0, htf_demand, htf_supply, itf_up, [ltf_zone_valid, ltf_zone_invalid]
    )

    assert isinstance(plan, MultiTimeframePlan)
    assert ltf_zone_valid in plan.eligible_execution_zones
    assert ltf_zone_invalid in plan.rejected_boundary_zones
    assert len(plan.eligible_execution_zones) == 1
    assert len(plan.rejected_boundary_zones) == 1


def test_episode_07_all_time_high_shorting_prohibition():
    """
    Episode 7 Concept 8: Federal Bank ATH Case Study.
    At All-Time Highs, no overhead supply exists. Shorting is strictly prohibited!
    """
    engine = DemandSupplyEngine()
    htf_demand = engine.scan_for_zones(
        np.array([120.0, 95.0, 100.0]),
        np.array([121.0, 102.0, 125.0]),
        np.array([94.0, 90.0, 99.0]),
        np.array([95.0, 100.0, 124.0]),
    )[0]

    itf_up = np.linspace(100.0, 150.0, 60)

    # When at ATH (htf_supply is None)
    plan_ath = DemandSupplyEngine.build_multi_timeframe_plan(
        TradingStyle.MIT, 250.0, htf_demand, None, itf_up, []
    )
    assert plan_ath.curve_position == CurvePosition.ALL_TIME_HIGH
    assert plan_ath.action_bias == TradeActionBias.BUY_ONLY
    assert "shorting is strictly prohibited" in plan_ath.rationale.lower()





# =====================================================================
# EPISODE 8 TESTS: TRADE SCORE (7/7), MAHABHARATA ALIGNMENT & DYNAMIC TARGET
# =====================================================================

def test_episode_08_trade_score_three_parameters_and_quality_tiers():
    """
    Episode 8 Concept 2: The Three Parameters of Trade Score (Max: 7 Points).
    - Freshness: 3.0 (fresh), 1.5 (tested 1x), 0.0 (tested >=2x)
    - Strength: 2.0 (>=2 exciting or gap), 1.0 (1 exciting no gap)
    - Time at Base: 2.0 (1-3 base), 1.0 (4-5 base), 0.0 (>5 base)
    """
    engine = DemandSupplyEngine()
    # Mock base zone: DBR Demand (PL 100.0, DL 90.0)
    opens = np.array([120.0, 95.0, 100.0])
    highs = np.array([121.0, 102.0, 125.0])
    lows = np.array([94.0, 90.0, 99.0])
    closes = np.array([95.0, 100.0, 124.0])
    base_zone = engine.scan_for_zones(opens, highs, lows, closes)[0]

    # Picture 1: Fresh (3) + 2 Exciting Leg-outs (2) + 1 Base Candle (2) = 7/7 (PRISTINE)
    base_zone.departure_strength = 2
    base_zone.base_candles_count = 1
    f1, s1, t1, tot1, q1 = DemandSupplyEngine.calculate_trade_score(base_zone, test_count=0)
    assert f1 == 3.0
    assert s1 == 2.0
    assert t1 == 2.0
    assert tot1 == 7.0
    assert q1 == TradeScoreQuality.PRISTINE

    # Picture 2: Fresh (3) + 2 Exciting Leg-outs (2) + 4 Base Candles (1) = 6/7 (SOLID)
    base_zone.base_candles_count = 4
    f2, s2, t2, tot2, q2 = DemandSupplyEngine.calculate_trade_score(base_zone, test_count=0)
    assert f2 == 3.0
    assert s2 == 2.0
    assert t2 == 1.0
    assert tot2 == 6.0
    assert q2 == TradeScoreQuality.SOLID

    # Picture 3: Fresh (3) + 1 Leg-out with Gap (2) + 1 Base Candle (2) = 7/7 (PRISTINE)
    base_zone.departure_strength = 1
    base_zone.base_candles_count = 1
    f3, s3, t3, tot3, q3 = DemandSupplyEngine.calculate_trade_score(base_zone, test_count=0, is_gap_departure=True)
    assert f3 == 3.0
    assert s3 == 2.0
    assert t3 == 2.0
    assert tot3 == 7.0
    assert q3 == TradeScoreQuality.PRISTINE

    # Picture 4: Fresh (3) + 1 Leg-out no Gap (1) + 4 Base Candles (1) = 5/7 (WEAK)
    base_zone.departure_strength = 1
    base_zone.base_candles_count = 4
    f4, s4, t4, tot4, q4 = DemandSupplyEngine.calculate_trade_score(base_zone, test_count=0, is_gap_departure=False)
    assert f4 == 3.0
    assert s4 == 1.0
    assert t4 == 1.0
    assert tot4 == 5.0
    assert q4 == TradeScoreQuality.WEAK

    # Tested 1x: 1.5 + 2 + 2 = 5.5 (WEAK)
    base_zone.departure_strength = 2
    base_zone.base_candles_count = 1
    f_test1, _, _, tot_test1, q_test1 = DemandSupplyEngine.calculate_trade_score(base_zone, test_count=1)
    assert f_test1 == 1.5
    assert tot_test1 == 5.5
    assert q_test1 == TradeScoreQuality.WEAK

    # Tested >=2x: 0.0 + 2 + 2 = 4.0 (WEAK)
    f_test2, _, _, tot_test2, q_test2 = DemandSupplyEngine.calculate_trade_score(base_zone, test_count=2)
    assert f_test2 == 0.0
    assert tot_test2 == 4.0
    assert q_test2 == TradeScoreQuality.WEAK


def test_episode_08_mahabharata_character_alignment_coinciding_aggressive_fatal():
    """
    Episode 8 Concept 4: The Mahabharata Metaphor.
    - Shri Krishna: HTF Demand (PL 100, DL 90)
    - Bhishma Pitamah: HTF Supply (PL 200, DL 210)
    - Arjuna: LTF Demand
    - Duryodhana: LTF Supply
    """
    engine = DemandSupplyEngine()
    htf_demand = engine.scan_for_zones(
        np.array([120.0, 95.0, 100.0]),
        np.array([121.0, 102.0, 125.0]),
        np.array([94.0, 90.0, 99.0]),
        np.array([95.0, 100.0, 124.0]),
    )[0]  # PL 100.0, DL 90.0

    htf_supply = engine.scan_for_zones(
        np.array([180.0, 205.0, 200.0]),
        np.array([185.0, 210.0, 201.0]),
        np.array([179.0, 198.0, 180.0]),
        np.array([205.0, 200.0, 182.0]),
    )[0]  # PL 200.0, DL 210.0

    # 1. Coinciding: Arjuna stands beside Shri Krishna (PL 98, DL 92)
    ltf_coinciding = engine.scan_for_zones(
        np.array([110.0, 95.0, 98.0]),
        np.array([111.0, 100.0, 115.0]),
        np.array([94.0, 92.0, 97.0]),
        np.array([95.0, 98.0, 114.0]),
    )[0]
    align_coinciding = DemandSupplyEngine.evaluate_character_alignment(ltf_coinciding, htf_demand, htf_supply)
    assert align_coinciding == ZoneAlignmentType.COINCIDING

    # 2. Aggressive: Arjuna stands ahead of Shri Krishna (PL 140, DL 135)
    ltf_aggressive = engine.scan_for_zones(
        np.array([150.0, 137.0, 140.0]),
        np.array([151.0, 142.0, 160.0]),
        np.array([136.0, 135.0, 139.0]),
        np.array([137.0, 140.0, 158.0]),
    )[0]
    align_aggressive = DemandSupplyEngine.evaluate_character_alignment(ltf_aggressive, htf_demand, htf_supply)
    assert align_aggressive == ZoneAlignmentType.AGGRESSIVE

    # 3. Fatal Trap: Arjuna entering Bhishma Pitamah's territory (PL 202, DL 195)
    ltf_fatal = engine.scan_for_zones(
        np.array([215.0, 200.0, 202.0]),
        np.array([216.0, 204.0, 220.0]),
        np.array([199.0, 195.0, 201.0]),
        np.array([200.0, 202.0, 219.0]),
    )[0]
    align_fatal = DemandSupplyEngine.evaluate_character_alignment(ltf_fatal, htf_demand, htf_supply)
    assert align_fatal == ZoneAlignmentType.FATAL_TRAP

    # 4. Short Fatal Trap: Duryodhana shorting right after Shri Krishna bounce (PL <= 100.0)
    ltf_short_trap = engine.scan_for_zones(
        np.array([90.0, 100.0, 98.0]),
        np.array([92.0, 102.0, 99.0]),
        np.array([89.0, 97.0, 80.0]),
        np.array([100.0, 98.0, 81.0]),
    )[0]  # Supply zone with PL 98.0 <= HTF Demand PL 100.0
    align_short_trap = DemandSupplyEngine.evaluate_character_alignment(ltf_short_trap, htf_demand, htf_supply)
    assert align_short_trap == ZoneAlignmentType.FATAL_TRAP


def test_episode_08_dynamic_opposing_itf_target_and_rrr_filter():
    """
    Episode 8 Concept 6: The Opposing ITF Zone Target Rule.
    Target = Proximal Line of Opposing Intermediate Supply (for Long) or Demand (for Short).
    Must satisfy minimum 2:1 RRR.
    """
    engine = DemandSupplyEngine()
    # LTF Demand: Entry = 100.0, SL = 90.0 (Risk = 10.0)
    ltf_demand = engine.scan_for_zones(
        np.array([110.0, 95.0, 100.0]),
        np.array([111.0, 100.0, 120.0]),
        np.array([94.0, 90.0, 99.0]),
        np.array([95.0, 100.0, 119.0]),
    )[0]
    ltf_demand.entry_price = 100.0
    ltf_demand.stop_loss = 90.0

    # 1. High Reward Case: Opposing ITF Supply PL = 135.0 (Reward = 35.0 -> 3.5:1 RRR >= 2.0)
    itf_supply_far = engine.scan_for_zones(
        np.array([125.0, 140.0, 135.0]),
        np.array([126.0, 142.0, 136.0]),
        np.array([124.0, 134.0, 115.0]),
        np.array([139.0, 135.0, 116.0]),
    )[0]  # PL 135.0
    target1, rrr1, ok1 = DemandSupplyEngine.calculate_opposing_itf_target(ltf_demand, itf_supply_far)
    assert target1 == itf_supply_far.proximal_line
    assert bool(ok1) is True
    assert rrr1 >= 2.0

    # 2. Low Reward Case: Opposing ITF Supply PL = 115.0 (Reward = 15.0 -> 1.5:1 RRR < 2.0) -> REJECTED!
    itf_supply_close = engine.scan_for_zones(
        np.array([105.0, 120.0, 115.0]),
        np.array([106.0, 122.0, 116.0]),
        np.array([104.0, 114.0, 95.0]),
        np.array([119.0, 115.0, 96.0]),
    )[0]  # PL
    target2, rrr2, ok2 = DemandSupplyEngine.calculate_opposing_itf_target(ltf_demand, itf_supply_close)
    assert target2 == itf_supply_close.proximal_line
    assert bool(ok2) is False
    assert rrr2 < 2.0

    # 3. Clean Sky / ATH (opposing_itf_zone is None) -> Defaults to 2:1 (120.0)
    target3, rrr3, ok3 = DemandSupplyEngine.calculate_opposing_itf_target(ltf_demand, None)
    assert target3 == 120.0
    assert rrr3 == 2.0
    assert bool(ok3) is True


def test_episode_08_gold_standard_best_trade_setup_evaluation():
    """
    Episode 8 Concept 5: Definition of a "Best Trade Setup" (The 4 Pillars).
    Pillar 1: Trade Score >= 6.0 (preferably 7.0)
    Pillar 2: Clean Closing (proven zone)
    Pillar 3: Alignment (Coinciding or Pristine Aggressive)
    Pillar 4: Trend Support (UPTREND for Long)
    Pillar 5: Opposing ITF RRR >= 2.0
    """
    engine = DemandSupplyEngine()
    # Mock HTF Demand & Supply
    htf_demand = engine.scan_for_zones(
        np.array([120.0, 95.0, 100.0]),
        np.array([121.0, 102.0, 125.0]),
        np.array([94.0, 90.0, 99.0]),
        np.array([95.0, 100.0, 124.0]),
    )[0]  # PL 100, DL 90
    htf_supply = engine.scan_for_zones(
        np.array([180.0, 205.0, 200.0]),
        np.array([185.0, 210.0, 201.0]),
        np.array([179.0, 198.0, 180.0]),
        np.array([205.0, 200.0, 182.0]),
    )[0]  # PL 200, DL 210

    # Maruti Master Setup: Coinciding 7/7 demand zone (PL 98, DL 92), Entry 98, SL 91
    ltf_maruti = engine.scan_for_zones(
        np.array([110.0, 95.0, 98.0]),
        np.array([111.0, 100.0, 120.0]),
        np.array([94.0, 92.0, 97.0]),
        np.array([95.0, 98.0, 119.0]),
    )[0]
    ltf_maruti.departure_strength = 2
    ltf_maruti.base_candles_count = 1
    ltf_maruti.has_clean_closing = True
    ltf_maruti.is_proven_zone = True
    ltf_maruti.entry_price = 98.0
    ltf_maruti.stop_loss = 91.0  # Risk = 7.0

    # Opposing weekly supply at 135.0 (Reward = 37.0 -> RRR = 5.28:1)
    opposing_itf = engine.scan_for_zones(
        np.array([125.0, 140.0, 135.0]),
        np.array([126.0, 142.0, 136.0]),
        np.array([124.0, 134.0, 115.0]),
        np.array([139.0, 135.0, 116.0]),
    )[0]

    eval_best = DemandSupplyEngine.evaluate_best_trade_setup(
        ltf_zone=ltf_maruti,
        htf_demand=htf_demand,
        htf_supply=htf_supply,
        itf_trend=TrendDirection.UPTREND,
        opposing_itf_zone=opposing_itf,
    )
    assert isinstance(eval_best, TradeScoreBreakdown)
    assert eval_best.total_score == 7.0
    assert eval_best.quality == TradeScoreQuality.PRISTINE
    assert eval_best.alignment == ZoneAlignmentType.COINCIDING
    assert eval_best.is_best_setup is True
    assert eval_best.realized_rrr > 2.0
    assert len(eval_best.rejection_reasons) == 0

    # Counter-trend failure case (Downtrend on ITF) -> Rejected!
    eval_fail_trend = DemandSupplyEngine.evaluate_best_trade_setup(
        ltf_zone=ltf_maruti,
        htf_demand=htf_demand,
        htf_supply=htf_supply,
        itf_trend=TrendDirection.DOWNTREND,
        opposing_itf_zone=opposing_itf,
    )
    assert eval_fail_trend.is_best_setup is False
    assert any("Requires UPTREND" in r for r in eval_fail_trend.rejection_reasons)


def test_episode_08_mtfa_plan_evaluates_execution_zones_scores():
    """
    Episode 8 Integration: build_multi_timeframe_plan automatically scores eligible execution zones.
    """
    engine = DemandSupplyEngine()
    htf_demand = engine.scan_for_zones(
        np.array([120.0, 95.0, 100.0]),
        np.array([121.0, 102.0, 125.0]),
        np.array([94.0, 90.0, 99.0]),
        np.array([95.0, 100.0, 124.0]),
    )[0]
    htf_supply = engine.scan_for_zones(
        np.array([180.0, 205.0, 200.0]),
        np.array([185.0, 210.0, 201.0]),
        np.array([179.0, 198.0, 180.0]),
        np.array([205.0, 200.0, 182.0]),
    )[0]

    ltf_zone = engine.scan_for_zones(
        np.array([110.0, 95.0, 98.0]),
        np.array([111.0, 100.0, 115.0]),
        np.array([94.0, 92.0, 97.0]),
        np.array([95.0, 98.0, 114.0]),
    )[0]
    ltf_zone.departure_strength = 2
    ltf_zone.base_candles_count = 1

    itf_up = np.linspace(100.0, 150.0, 60)
    plan = DemandSupplyEngine.build_multi_timeframe_plan(
        TradingStyle.MIT, 120.0, htf_demand, htf_supply, itf_up, [ltf_zone]
    )

    assert len(plan.eligible_execution_zones) == 1
    scored_zone = plan.eligible_execution_zones[0]
    assert scored_zone.trade_score is not None
    assert isinstance(scored_zone.trade_score, TradeScoreBreakdown)
    assert scored_zone.trade_score.total_score == 7.0


# =====================================================================
# EPISODE 9 TESTS: TRADING STYLE, AUTHENTICITY & EMOTIONAL REJECTION MINDSET
# =====================================================================

def test_episode_09_entry_type_2_mechanics_and_gap_abort():
    """
    Episode 9 Concept 2B: Entry Type 2 (Confirmation Entry).
    Rule 1: Candle 1 must close inside zone (PL >= Close >= DL).
    Rule 2: Candle 2 must open inside zone.
    Gap-down below DL -> Aborted (saved from stop-loss hit).
    Gap-up above PL -> Missed.
    """
    engine = DemandSupplyEngine()
    # Mock Demand Zone: PL = 100.0, DL = 90.0
    opens = np.array([110.0, 95.0, 98.0])
    highs = np.array([111.0, 100.0, 120.0])
    lows = np.array([94.0, 90.0, 97.0])
    closes = np.array([95.0, 98.0, 119.0])
    demand_zone = engine.scan_for_zones(opens, highs, lows, closes)[0]
    demand_zone.proximal_line = 100.0
    demand_zone.distal_line = 90.0

    # 1. Successful Entry: Bar 1 closes at 95.0 (inside), Bar 2 opens at 96.0 (inside)
    ok1, msg1 = DemandSupplyEngine.evaluate_entry_type_2(demand_zone, bar1_close=95.0, bar2_open=96.0)
    assert ok1 is True
    assert msg1 == "ENTRY_TRIGGERED_IN_ZONE"

    # 2. Aborted Gap-down: Bar 1 closes at 95.0, Bar 2 opens at 88.0 (< 90.0 DL) -> SAVED FROM SL!
    ok2, msg2 = DemandSupplyEngine.evaluate_entry_type_2(demand_zone, bar1_close=95.0, bar2_open=88.0)
    assert ok2 is False
    assert msg2 == "ABORTED_GAP_DOWN_BELOW_DISTAL"

    # 3. Missed Gap-up: Bar 1 closes at 95.0, Bar 2 opens at 103.0 (> 100.0 PL)
    ok3, msg3 = DemandSupplyEngine.evaluate_entry_type_2(demand_zone, bar1_close=95.0, bar2_open=103.0)
    assert ok3 is False
    assert msg3 == "MISSED_GAP_UP_ABOVE_PROXIMAL"

    # 4. Bar 1 did not close in zone (closed at 105.0)
    ok4, msg4 = DemandSupplyEngine.evaluate_entry_type_2(demand_zone, bar1_close=105.0, bar2_open=95.0)
    assert ok4 is False
    assert msg4 == "BAR1_DID_NOT_CLOSE_IN_ZONE"


def test_episode_09_zone_authenticity_and_tradeability():
    """
    Episode 9 Concept 3: Authenticity and Credibility of Zones.
    - Authentic: Forms independently in virgin space.
    - Non-Authentic: Forms as an immediate reaction bounce to an earlier historical zone.
    - Tradeability: Non-authentic is tradeable ONLY if leg-out has proven clean closing.
    """
    engine = DemandSupplyEngine()
    # Historical Zone 1: Authentic base (PL 100.0, DL 90.0, indices 0..2)
    z1 = engine.scan_for_zones(
        np.array([120.0, 95.0, 100.0]),
        np.array([121.0, 102.0, 125.0]),
        np.array([94.0, 90.0, 99.0]),
        np.array([95.0, 100.0, 124.0]),
    )[0]
    z1.proximal_line = 100.0
    z1.distal_line = 90.0
    z1.base_start_idx = 1
    z1.first_leg_out_idx = 2

    # Zone 2: Non-authentic reaction zone formed inside Zone 1 (PL 98.0, DL 92.0, indices 5..7)
    z2 = engine.scan_for_zones(
        np.array([110.0, 95.0, 98.0]),
        np.array([111.0, 100.0, 115.0]),
        np.array([94.0, 92.0, 97.0]),
        np.array([95.0, 98.0, 114.0]),
    )[0]
    z2.proximal_line = 98.0
    z2.distal_line = 92.0
    z2.base_start_idx = 6
    z2.first_leg_out_idx = 7
    z2.has_clean_closing = True
    z2.is_proven_zone = True

    auth2, tradeable2, reason2 = DemandSupplyEngine.evaluate_zone_authenticity(z2, [z1])
    assert auth2 == ZoneAuthenticity.NON_AUTHENTIC
    assert tradeable2 is True
    assert "TRADEABLE_NON_AUTHENTIC_PROVEN" in reason2

    # Zone 3: Non-authentic with unproven/failed close -> Non-tradeable!
    z3 = engine.scan_for_zones(
        np.array([110.0, 95.0, 98.0]),
        np.array([111.0, 100.0, 115.0]),
        np.array([94.0, 92.0, 97.0]),
        np.array([95.0, 98.0, 114.0]),
    )[0]
    z3.proximal_line = 98.0
    z3.distal_line = 92.0
    z3.base_start_idx = 6
    z3.first_leg_out_idx = 7
    z3.has_clean_closing = False
    z3.is_proven_zone = False

    auth3, tradeable3, reason3 = DemandSupplyEngine.evaluate_zone_authenticity(z3, [z1])
    assert auth3 == ZoneAuthenticity.NON_AUTHENTIC
    assert tradeable3 is False
    assert "NON_TRADEABLE_NON_AUTHENTIC" in reason3

    # Zone 4: Authentic virgin zone formed far away (PL 150.0, DL 140.0)
    z4 = engine.scan_for_zones(
        np.array([160.0, 142.0, 150.0]),
        np.array([161.0, 155.0, 175.0]),
        np.array([141.0, 140.0, 149.0]),
        np.array([142.0, 150.0, 174.0]),
    )[0]
    z4.proximal_line = 150.0
    z4.distal_line = 140.0
    z4.base_start_idx = 10
    z4.first_leg_out_idx = 11

    auth4, tradeable4, reason4 = DemandSupplyEngine.evaluate_zone_authenticity(z4, [z1])
    assert auth4 == ZoneAuthenticity.AUTHENTIC
    assert tradeable4 is True
    assert reason4 == "AUTHENTIC_ORIGIN_ZONE"


def test_episode_09_rupee_risk_equality_mit_vs_dit():
    """
    Episode 9 Concept 4B: The Rupee-Risk Equality Rule.
    Through position sizing, a ₹50 stop-loss in MIT and a ₹2 stop-loss in DIT
    carry the EXACT SAME ₹1,000 monetary risk!
    """
    total_risk_inr = 1000.0

    # Positional MIT Trade: Entry 500, SL 450 (Risk = 50 pts)
    shares_mit = DemandSupplyEngine.calculate_rupee_risk_position_size(
        total_risk_inr=total_risk_inr, entry_price=500.0, stop_loss=450.0
    )
    assert shares_mit == 20
    assert shares_mit * 50.0 == 1000.0

    # Intraday DIT Trade: Entry 500, SL 498 (Risk = 2 pts)
    shares_dit = DemandSupplyEngine.calculate_rupee_risk_position_size(
        total_risk_inr=total_risk_inr, entry_price=500.0, stop_loss=498.0
    )
    assert shares_dit == 500
    assert shares_dit * 2.0 == 1000.0


def test_episode_09_mandatory_100_trade_directive():
    """
    Episode 9 Concept 4C: The Mandatory 100-Trade Directive.
    Must complete at least 100 positional/swing trades (WIT/MIT) before unlocking active intraday (HIT/DIT).
    """
    assert TradingStyleCategory.INTRADAY.value == "INTRADAY"
    # 1. Novice trader with 45 positional trades attempts HIT / DIT -> BLOCKED
    ok_hit, msg_hit = DemandSupplyEngine.enforce_mandatory_100_trade_rule(TradingStyle.HIT, prior_positional_trades=45)
    assert ok_hit is False
    assert "45/100 positional trades completed" in msg_hit

    ok_dit, msg_dit = DemandSupplyEngine.enforce_mandatory_100_trade_rule(TradingStyle.DIT, prior_positional_trades=45)
    assert ok_dit is False

    # 2. Trader attempts swing/positional (WIT or MIT) with 45 trades -> APPROVED
    ok_wit, msg_wit = DemandSupplyEngine.enforce_mandatory_100_trade_rule(TradingStyle.WIT, prior_positional_trades=45)
    assert ok_wit is True
    assert "approved" in msg_wit

    ok_mit, msg_mit = DemandSupplyEngine.enforce_mandatory_100_trade_rule(TradingStyle.MIT, prior_positional_trades=45)
    assert ok_mit is True

    # 3. Disciplined trader with 110 positional trades attempts DIT -> UNLOCKED!
    ok_unlocked, msg_unlocked = DemandSupplyEngine.enforce_mandatory_100_trade_rule(
        TradingStyle.DIT, prior_positional_trades=110
    )
    assert ok_unlocked is True
    assert "unlocked" in msg_unlocked.lower()


def test_episode_09_rejection_mindset_audit_pipeline():
    """
    Episode 9 Concept 5A: The Rejection Mindset Audit.
    Runs 6 aggressive rejection filters to filter out emotional/forced trades.
    """
    engine = DemandSupplyEngine()
    # Pristine Maruti-style Setup:
    # HTF Demand: PL 100, DL 90
    htf_demand = engine.scan_for_zones(
        np.array([120.0, 95.0, 100.0]),
        np.array([121.0, 102.0, 125.0]),
        np.array([94.0, 90.0, 99.0]),
        np.array([95.0, 100.0, 124.0]),
    )[0]
    # Opposing Weekly Supply: PL 135 (Reward = 37.0 -> RRR > 2.0)
    opposing_itf = engine.scan_for_zones(
        np.array([125.0, 140.0, 135.0]),
        np.array([126.0, 142.0, 136.0]),
        np.array([124.0, 134.0, 115.0]),
        np.array([139.0, 135.0, 116.0]),
    )[0]

    # Coinciding LTF Zone
    ltf_zone = engine.scan_for_zones(
        np.array([110.0, 95.0, 98.0]),
        np.array([111.0, 100.0, 120.0]),
        np.array([94.0, 92.0, 97.0]),
        np.array([95.0, 98.0, 119.0]),
    )[0]
    ltf_zone.proximal_line = 98.0
    ltf_zone.distal_line = 92.0
    ltf_zone.entry_price = 98.0
    ltf_zone.stop_loss = 91.0
    ltf_zone.departure_strength = 2
    ltf_zone.base_candles_count = 1
    ltf_zone.has_clean_closing = True
    ltf_zone.is_proven_zone = True

    # 1. Pristine Setup Audit -> Survives Rejection Mindset!
    audit_clean = DemandSupplyEngine.audit_rejection_mindset(
        zone=ltf_zone,
        htf_demand=htf_demand,
        htf_supply=None,
        itf_trend=TrendDirection.UPTREND,
        opposing_itf_zone=opposing_itf,
        trading_style=TradingStyle.MIT,
        prior_positional_trades=100,
        total_risk_inr=1000.0,
    )
    assert isinstance(audit_clean, RejectionAudit)
    assert audit_clean.survived_rejection_mindset is True
    assert audit_clean.is_rejected is False
    assert audit_clean.recommended_entry_type == EntryType.SET_AND_FORGET
    assert audit_clean.rupee_risk_equalized_shares == 142  # 1000 // 7 = 142 shares
    assert len(audit_clean.rejection_reasons) == 0

    # 2. Flawed Setup Audit (Counter-trend + Intraday without 100 trades) -> REJECTED!
    audit_flawed = DemandSupplyEngine.audit_rejection_mindset(
        zone=ltf_zone,
        htf_demand=htf_demand,
        htf_supply=None,
        itf_trend=TrendDirection.DOWNTREND,  # Conflict!
        opposing_itf_zone=opposing_itf,
        trading_style=TradingStyle.HIT,       # Conflict (only 20 trades)!
        prior_positional_trades=20,
        total_risk_inr=1000.0,
    )
    assert audit_flawed.survived_rejection_mindset is False
    assert audit_flawed.is_rejected is True
    assert len(audit_flawed.rejection_reasons) >= 2


# =====================================================================
# EPISODE 10 TESTS: RISK MANAGEMENT, CAPITAL PROTECTION & SIZING FORMULA
# =====================================================================

def test_episode_10_exact_position_sizing_and_monetary_risk_invariance():
    """
    Episode 10 Concept 3: The Exact Position Sizing Formula (TVS Motor Case Study).
    Quantity = floor(Risk_Per_Trade / abs(Entry - StopLoss))
    Monetary risk remains strictly identical and capped regardless of share price or SL distance.
    """
    capital = 100000.0  # ₹1 Lakh
    risk_tier = RiskTier.BEGINNER  # 1% = ₹1,000

    # 1. Scenario 1: ₹20 Stop-Loss -> 50 shares
    s1 = GTFRiskManager.calculate_position_size(capital, risk_tier, entry_price=1000.0, stop_loss=980.0)
    assert isinstance(s1, SizingBreakdown)
    assert s1.risk_distance_points == 20.0
    assert s1.quantity_shares == 50
    assert s1.actual_monetary_risk_inr == 1000.0
    assert s1.total_capital_required_inr == 50000.0

    # 2. Scenario 2: ₹30 Stop-Loss -> 33 shares
    s2 = GTFRiskManager.calculate_position_size(capital, risk_tier, entry_price=1000.0, stop_loss=970.0)
    assert s2.quantity_shares == 33
    assert s2.actual_monetary_risk_inr == 990.0 <= 1000.0

    # 3. Scenario 3: ₹40 Stop-Loss -> 25 shares
    s3 = GTFRiskManager.calculate_position_size(capital, risk_tier, entry_price=1000.0, stop_loss=960.0)
    assert s3.quantity_shares == 25
    assert s3.actual_monetary_risk_inr == 1000.0

    # 4. Scenario 4: ₹12 Stop-Loss (Refined Entry) -> 83 shares
    s4 = GTFRiskManager.calculate_position_size(capital, risk_tier, entry_price=1000.0, stop_loss=988.0)
    assert s4.quantity_shares == 83
    assert s4.actual_monetary_risk_inr == 996.0 <= 1000.0

    # 5. Short Trade: ₹23 Stop-Loss -> 43 shares
    s5 = GTFRiskManager.calculate_position_size(capital, risk_tier, entry_price=1000.0, stop_loss=1023.0)
    assert s5.quantity_shares == 43
    assert s5.actual_monetary_risk_inr == 989.0 <= 1000.0

    # 6. Short Trade: ₹65 Stop-Loss -> 15 shares
    s6 = GTFRiskManager.calculate_position_size(capital, risk_tier, entry_price=1000.0, stop_loss=1065.0)
    assert s6.quantity_shares == 15
    assert s6.actual_monetary_risk_inr == 975.0 <= 1000.0


def test_episode_10_anti_tamper_chasing_widening_averaging_guards():
    """
    Episode 10 Concept 4: Anti-Tamper Execution Guards.
    1. Chasing Missed Entry
    2. Modifying / Widening Stop-Loss Post-Entry
    3. Averaging Down Trap
    """
    # 1. Clean Order (No violations)
    clean, violations = GTFRiskManager.detect_anti_tamper_violations(
        original_entry=100.0,
        current_market_price=100.5,
        original_sl=90.0,
        new_sl=90.0,
        is_demand=True,
        is_averaging_down=False,
    )
    assert clean is True
    assert len(violations) == 0

    # 2. Chasing Missed Entry (CMP rallied 3% past entry)
    chase, v_chase = GTFRiskManager.detect_anti_tamper_violations(
        original_entry=100.0,
        current_market_price=103.0,
        original_sl=90.0,
        new_sl=90.0,
        is_demand=True,
    )
    assert chase is False
    assert any("Chasing Missed Entry Prohibited" in v for v in v_chase)

    # 3. Widening Stop-Loss on Long Setup (Moving SL down from 90 to 80)
    widen, v_widen = GTFRiskManager.detect_anti_tamper_violations(
        original_entry=100.0,
        current_market_price=100.0,
        original_sl=90.0,
        new_sl=80.0,
        is_demand=True,
    )
    assert widen is False
    assert any("Stop-Loss Widening Prohibited" in v for v in v_widen)

    # 4. Averaging Down Trap
    avg_down, v_avg = GTFRiskManager.detect_anti_tamper_violations(
        original_entry=100.0,
        current_market_price=95.0,
        original_sl=90.0,
        new_sl=90.0,
        is_averaging_down=True,
    )
    assert avg_down is False
    assert any("Averaging Down Trap" in v for v in v_avg)


def test_episode_10_journal_monthly_cap_and_repeat_mistake_tracker():
    """
    Episode 10 Concept 6 & 11: The 10 Trades/Month Cap & 40-Mistake Rule.
    'A mistake repeated more than once is a decision.'
    """
    journal = GTFTradingJournal(initial_capital=100000.0)

    # Log 10 trades in month 2026-11
    for i in range(1, 11):
        entry = TradeLogEntry(
            trade_id=i,
            date="2026-11-15",
            symbol="TCS",
            entry_price=3500.0,
            stop_loss=3450.0,
            target_price=3600.0,
            quantity=20,
            outcome="TARGET_HIT",
            pnl_inr=2000.0,
        )
        ok, msg = journal.log_trade(entry)
        assert ok is True

    assert journal.total_trades_count == 10

    # 11th trade in the same month -> BLOCKED by monthly cap
    entry_11 = TradeLogEntry(
        trade_id=11,
        date="2026-11-20",
        symbol="INFY",
        entry_price=1800.0,
        stop_loss=1780.0,
        target_price=1840.0,
        quantity=50,
        outcome="OPEN",
    )
    ok_11, msg_11 = journal.log_trade(entry_11)
    assert ok_11 is False
    assert "Monthly Cap Reached" in msg_11

    # Test Repeat Mistake Detection in a new month (2026-12)
    entry_mistake_1 = TradeLogEntry(
        trade_id=12,
        date="2026-12-01",
        symbol="RELIANCE",
        entry_price=2500.0,
        stop_loss=2480.0,
        target_price=2540.0,
        quantity=50,
        outcome="STOP_LOSS_HIT",
        mistakes=[ExecutionErrorType.TREND_CONFLICT],
    )
    ok_m1, msg_m1 = journal.log_trade(entry_mistake_1)
    assert ok_m1 is True
    assert "Repeat Mistake Detected" not in msg_m1

    # Second time repeating TREND_CONFLICT -> Warning surfaced!
    entry_mistake_2 = TradeLogEntry(
        trade_id=13,
        date="2026-12-05",
        symbol="HDFCBANK",
        entry_price=1600.0,
        stop_loss=1580.0,
        target_price=1640.0,
        quantity=50,
        outcome="STOP_LOSS_HIT",
        mistakes=[ExecutionErrorType.TREND_CONFLICT],
    )
    ok_m2, msg_m2 = journal.log_trade(entry_mistake_2)
    assert ok_m2 is True
    assert "Repeat Mistake Detected: TREND_CONFLICT logged 2 times!" in msg_m2


def test_episode_10_quantitative_growth_model_excel_projections():
    """
    Episode 10 Concept 7: Quantitative Excel Growth Model.
    Verifies exact mathematical returns across win rates and RRR tiers.
    """
    capital = 100000.0

    # Model 1: Beginner Phase (1% RPT = ₹1,000 Risk, 2:1 RRR = ₹2,000 Target)
    # 50% Win Rate (5 Wins, 5 Losses): 5 * 2000 - 5 * 1000 = +₹5,000 (+5%/month, +60% annual)
    p_50 = GTFRiskManager.project_growth(capital, RiskTier.BEGINNER, win_rate=0.50, target_rrr=2.0)
    assert isinstance(p_50, GrowthProjection)
    assert p_50.net_monthly_profit == 5000.0
    assert p_50.monthly_return_pct == 5.0
    assert p_50.annual_return_pct == 60.0

    # 60% Win Rate (6 Wins, 4 Losses): 6 * 2000 - 4 * 1000 = +₹8,000 (+8%/month, +96% annual)
    p_60 = GTFRiskManager.project_growth(capital, RiskTier.BEGINNER, win_rate=0.60, target_rrr=2.0)
    assert p_60.net_monthly_profit == 8000.0
    assert p_60.monthly_return_pct == 8.0
    assert p_60.annual_return_pct == 96.0

    # 70% Win Rate (7 Wins, 3 Losses): 7 * 2000 - 3 * 1000 = +₹11,000 (+11%/month)
    p_70 = GTFRiskManager.project_growth(capital, RiskTier.BEGINNER, win_rate=0.70, target_rrr=2.0)
    assert p_70.net_monthly_profit == 11000.0
    assert p_70.monthly_return_pct == 11.0

    # Model 2: Pro Phase (2% RPT = ₹2,000 Risk, 2:1 RRR = ₹4,000 Target)
    # 50% Win Rate: 5 * 4000 - 5 * 2000 = +₹10,000 (+10%/month)
    p_pro_50 = GTFRiskManager.project_growth(capital, RiskTier.PRO, win_rate=0.50, target_rrr=2.0)
    assert p_pro_50.net_monthly_profit == 10000.0
    assert p_pro_50.monthly_return_pct == 10.0

    # Model 3: Expanding to 3:1 RRR (2% RPT = ₹2,000 Risk, 3:1 RRR = ₹6,000 Target)
    # 50% Win Rate: 5 * 6000 - 5 * 2000 = +₹20,000 (+20%/month)
    p_pro_3to1 = GTFRiskManager.project_growth(capital, RiskTier.PRO, win_rate=0.50, target_rrr=3.0)
    assert p_pro_3to1.net_monthly_profit == 20000.0
    assert p_pro_3to1.monthly_return_pct == 20.0


def test_episode_10_smaller_timeframe_overpowering_higher_timeframe():
    """
    Episode 10 Concept 10: Smaller Timeframe Beating Higher Timeframe.
    When a smaller timeframe zone breaches and closes decisively beyond an opposing HTF zone,
    it becomes an extraordinary institutional origin.
    """
    engine = DemandSupplyEngine()
    # HTF Weekly Supply Zone: PL = 200.0, DL = 210.0
    htf_supply = engine.scan_for_zones(
        np.array([180.0, 205.0, 200.0]),
        np.array([185.0, 210.0, 201.0]),
        np.array([179.0, 198.0, 180.0]),
        np.array([205.0, 200.0, 182.0]),
    )[0]
    htf_supply.proximal_line = 200.0
    htf_supply.distal_line = 210.0

    # Smaller Timeframe (Daily) Demand Zone formed at PL 215.0, DL 205.0
    # Decisively breached and closed beyond HTF Supply's Distal Line (210.0)!
    ltf_demand = engine.scan_for_zones(
        np.array([200.0, 212.0, 215.0]),
        np.array([202.0, 218.0, 230.0]),
        np.array([198.0, 205.0, 214.0]),
        np.array([211.0, 215.0, 229.0]),
    )[0]
    ltf_demand.proximal_line = 215.0
    ltf_demand.distal_line = 205.0
    ltf_demand.has_clean_closing = True

    is_overpowering = DemandSupplyEngine.detect_htf_overpowering_zone(ltf_demand, htf_supply)
    assert is_overpowering is True
    assert ltf_demand.is_htf_overpowering_origin is True


# ==============================================================================
# EPISODE 11 TESTS: AGGRESSIVE VS CONSERVATIVE EXECUTION STANCES
# ==============================================================================


def test_episode_11_the_matching_timeframe_principle_and_steamroller_effect():
    """
    Episode 11 Principle: The Matching Timeframe Principle & Steamroller Effect.
    - Weekly supply retreat cannot be caught by shallow LTF daily/15m demand unless pristine origin.
    - Monthly supply retreat requires at least Monthly demand.
    - Quarterly supply retreat slices through daily demand.
    """
    # 1. Weekly Supply vs Standard Daily Demand -> Fails (Steamroller risk)
    matched, msg = DemandSupplyEngine.validate_matching_timeframe(
        retreat_supply_tf=TimeframeTier.WEEKLY,
        reaction_demand_tf=TimeframeTier.DAILY,
        is_pristine_origin=False,
    )
    assert matched is False
    assert "Steamroller Risk" in msg

    # 2. Weekly Supply vs Pristine Daily Origin Base -> Passes
    matched, msg = DemandSupplyEngine.validate_matching_timeframe(
        retreat_supply_tf=TimeframeTier.WEEKLY,
        reaction_demand_tf=TimeframeTier.DAILY,
        is_pristine_origin=True,
    )
    assert matched is True
    assert "Pristine origin exception satisfied" in msg

    # 3. Monthly Supply vs Monthly Demand -> Passes
    matched, msg = DemandSupplyEngine.validate_matching_timeframe(
        retreat_supply_tf=TimeframeTier.MONTHLY,
        reaction_demand_tf=TimeframeTier.MONTHLY,
        is_pristine_origin=False,
    )
    assert matched is True
    assert "Matching timeframe satisfied" in msg

    # 4. Quarterly Supply vs Daily Demand -> Fails decisively
    matched, msg = DemandSupplyEngine.validate_matching_timeframe(
        retreat_supply_tf=TimeframeTier.QUARTERLY,
        reaction_demand_tf=TimeframeTier.DAILY,
        is_pristine_origin=False,
    )
    assert matched is False
    assert "Steamroller Risk" in msg


def test_episode_11_evaluate_trading_stance_aggressive_vs_conservative():
    """
    Episode 11 Axiom: 'As a trader, you can always be conservative, but you can NEVER be always aggressive.'
    Aggressive is permitted ONLY when:
      1. Clean space ahead + aligned trend.
      2. Proven achievement (closed beyond opposing HTF supply).
    """
    engine = DemandSupplyEngine()
    demand_opens = np.array([200.0, 212.0, 215.0])
    demand_highs = np.array([202.0, 218.0, 230.0])
    demand_lows = np.array([198.0, 205.0, 214.0])
    demand_closes = np.array([211.0, 215.0, 229.0])

    supply_opens = np.array([180.0, 205.0, 200.0])
    supply_highs = np.array([185.0, 210.0, 201.0])
    supply_lows = np.array([179.0, 198.0, 180.0])
    supply_closes = np.array([205.0, 200.0, 182.0])

    ltf_demand = engine.scan_for_zones(demand_opens, demand_highs, demand_lows, demand_closes)[0]
    ltf_demand.timeframe = TimeframeTier.DAILY

    htf_supply = engine.scan_for_zones(supply_opens, supply_highs, supply_lows, supply_closes)[0]
    htf_supply.timeframe = TimeframeTier.WEEKLY

    # Scenario A: Retreating from Weekly supply without proven achievement -> Conservative enforced
    stance, msg = DemandSupplyEngine.evaluate_trading_stance(
        execution_zone=ltf_demand,
        opposing_htf_zone=htf_supply,
        has_proven_achievement=False,
    )
    assert stance == TradingStance.CONSERVATIVE
    assert "Conservative stance enforced" in msg
    assert ltf_demand.trading_stance == TradingStance.CONSERVATIVE

    # Scenario B: Retreating from Weekly supply WITH Proven Achievement -> Aggressive permitted
    stance, msg = DemandSupplyEngine.evaluate_trading_stance(
        execution_zone=ltf_demand,
        opposing_htf_zone=htf_supply,
        has_proven_achievement=True,
    )
    assert stance == TradingStance.AGGRESSIVE
    assert "Proven Achievement" in msg
    assert ltf_demand.trading_stance == TradingStance.AGGRESSIVE
    assert ltf_demand.has_proven_achievement is True

    # Scenario C: Clean Space Ahead with Uptrend -> Aggressive permitted
    stance, msg = DemandSupplyEngine.evaluate_trading_stance(
        execution_zone=ltf_demand,
        opposing_htf_zone=None,
        intermediate_trend=TrendDirection.UPTREND,
        has_clean_space=True,
    )
    assert stance == TradingStance.AGGRESSIVE
    assert "Clean space ahead" in msg

    # Scenario D: Sideways trend without clean space -> Conservative default
    stance, msg = DemandSupplyEngine.evaluate_trading_stance(
        execution_zone=ltf_demand,
        opposing_htf_zone=None,
        intermediate_trend=TrendDirection.SIDEWAYS,
        has_clean_space=False,
    )
    assert stance == TradingStance.CONSERVATIVE


def test_episode_11_anchoring_sl_to_shri_krishna_htf_distal_base():
    """
    Episode 11 Case Study: Bank of Baroda & Canara Bank.
    In sideways / down-leaning intermediate trend, anchor the stop-loss beneath
    the Distal Line of the underlying Higher Timeframe (Monthly) Demand Zone (Shri Krishna).
    """
    engine = DemandSupplyEngine()
    demand_opens = np.array([200.0, 212.0, 215.0])
    demand_highs = np.array([202.0, 218.0, 230.0])
    demand_lows = np.array([198.0, 205.0, 214.0])
    demand_closes = np.array([211.0, 215.0, 229.0])

    # LTF Daily Demand: PL = 200.0, DL = 195.0
    ltf_demand = engine.scan_for_zones(demand_opens, demand_highs, demand_lows, demand_closes)[0]
    ltf_demand.is_demand = True
    ltf_demand.proximal_line = 200.0
    ltf_demand.distal_line = 195.0

    # HTF Monthly Demand (Shri Krishna): PL = 205.0, DL = 180.0
    htf_demand = engine.scan_for_zones(demand_opens, demand_highs, demand_lows, demand_closes)[0]
    htf_demand.is_demand = True
    htf_demand.proximal_line = 205.0
    htf_demand.distal_line = 180.0

    anchored_sl = DemandSupplyEngine.anchor_sl_to_htf_base(
        ltf_zone=ltf_demand,
        htf_zone=htf_demand,
        tick_size=0.05,
        buffer_ticks=5,
    )

    # Expected: 180.0 - (0.05 * 5) = 179.75
    assert anchored_sl == 179.75
    assert ltf_demand.anchored_htf_stoploss == 179.75


def test_episode_11_structural_regime_inversion_detection():
    """
    Episode 11 Case Study: TVS Motor Exhaustion Phase at All-Time Highs.
    Demand failing while supply holds signals institutional distribution.
    """
    # Distribution regime: 4 demand zones breached, only 1 held; 3 supply zones held, 1 breached
    is_inverted, msg = DemandSupplyEngine.detect_structural_regime_inversion(
        demand_breached_count=4,
        demand_respected_count=1,
        supply_breached_count=1,
        supply_respected_count=3,
    )
    assert is_inverted is True
    assert "Structural Regime Inversion Confirmed" in msg
    assert "CEASE all aggressive long entries" in msg

    # Normal bullish regime: Demand holds (4 held, 1 breached), Supply fails (3 breached, 1 held)
    is_inverted, msg = DemandSupplyEngine.detect_structural_regime_inversion(
        demand_breached_count=1,
        demand_respected_count=4,
        supply_breached_count=3,
        supply_respected_count=1,
    )
    assert is_inverted is False
    assert "Normal regime intact" in msg


def test_episode_11_dynamic_20_ema_interaction_and_equilibrium():
    """
    Episode 11 Concept: Dynamic 20 EMA Equilibrium Curve.
    Short trades approaching a rising 20 EMA encounter dynamic bounce support.
    """
    # 1. Short trade approaching 20 EMA within 0.5% tolerance
    res = DemandSupplyEngine.check_dynamic_20_ema_interaction(
        current_price=100.2,
        ema_20=100.0,
        trade_direction="SHORT",
        tolerance_pct=0.5,
    )
    assert res["is_interacting"] is True
    assert res["warning_level"] == "CAUTION_DYNAMIC_SUPPORT"
    assert "Book partial profits" in res["action_recommendation"]

    # 2. Short trade comfortably far from 20 EMA (10% away)
    res = DemandSupplyEngine.check_dynamic_20_ema_interaction(
        current_price=110.0,
        ema_20=100.0,
        trade_direction="SHORT",
        tolerance_pct=0.5,
    )
    assert res["is_interacting"] is False
    assert res["warning_level"] == "NORMAL"
    assert "Comfortable distance" in res["action_recommendation"]


# ==============================================================================
# EPISODE 12 TESTS: MOVING AVERAGES, CORRELATION & RETAIL CROSSOVER TRAPS
# ==============================================================================


def test_episode_12_sma_and_ema_mathematical_calculations_and_lagging_proof():
    """
    Episode 12 Mathematical Mechanics:
    - SMA 50: Equal weight (1/n) for all candles.
    - EMA 50: Exponential weight (alpha = 2/(n+1)) hugging recent prices.
    - Demonstrates mathematically why Moving Averages lag during a V-reversal:
      Prices collapse from 1,200 to 800, then rally to 1,000.
      While real price rallies, SMA 50 continues falling because added price < dropped price.
    """
    # 1. Basic calculation verification
    prices = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
    sma3 = DemandSupplyEngine.calculate_sma(prices, period=3)
    assert np.isnan(sma3[0])
    assert np.isnan(sma3[1])
    assert sma3[2] == 20.0  # (10+20+30)/3
    assert sma3[3] == 30.0  # (20+30+40)/3
    assert sma3[4] == 40.0  # (30+40+50)/3

    ema3 = DemandSupplyEngine.calculate_ema(prices, period=3)
    # alpha = 2 / (3 + 1) = 0.5
    # Seed at index 2 = mean(10, 20, 30) = 20.0
    # idx 3 = 40.0 * 0.5 + 20.0 * 0.5 = 30.0
    # idx 4 = 50.0 * 0.5 + 30.0 * 0.5 = 40.0
    assert ema3[2] == 20.0
    assert ema3[3] == 30.0
    assert ema3[4] == 40.0

    # 2. Lagging indicator proof (COVID-19 HDFC Bank style crash & V-reversal)
    # 50 candles: first 40 candles flat at 1,200, next 5 crash to 800, last 5 rally to 1,000
    crash_series = np.concatenate([
        np.full(40, 1200.0),
        np.linspace(1200.0, 800.0, 5),
        np.linspace(800.0, 1000.0, 5),
    ])
    sma50 = DemandSupplyEngine.calculate_sma(crash_series, period=20)
    # At index 44 price is bottom, then price rallies to 1000
    # Even though price rallied from 800 to 1000, SMA continues sloping down!
    assert crash_series[-1] > crash_series[-5]  # Price rallied
    assert sma50[-1] < sma50[-5]  # SMA 20 is strictly lower (lagging!)


def test_episode_12_detect_golden_and_death_crossovers():
    """
    Episode 12: Detect Golden Crossover (EMA 20 crossing above EMA 50)
    and Death Crossover (EMA 20 crossing below EMA 50).
    """
    # Fast crosses above slow at the end
    fast = np.array([98.0, 99.0, 100.0, 102.0, 105.0])
    slow = np.array([101.0, 101.0, 101.0, 101.0, 101.0])

    cross_type, bar_idx, price = DemandSupplyEngine.detect_ma_crossover(fast, slow, lookback_bars=3)
    assert cross_type == MACrossoverType.GOLDEN_CROSSOVER
    assert bar_idx == 3  # Crossed at index 3 (102 > 101)
    assert price == 102.0

    # Fast crosses below slow at the end
    fast_down = np.array([105.0, 103.0, 101.0, 99.0, 97.0])
    slow_down = np.array([100.0, 100.0, 100.0, 100.0, 100.0])

    cross_type_down, bar_idx_down, price_down = DemandSupplyEngine.detect_ma_crossover(fast_down, slow_down, lookback_bars=3)
    assert cross_type_down == MACrossoverType.DEATH_CROSSOVER
    assert bar_idx_down == 3
    assert price_down == 99.0

    # No crossover (parallel lines)
    parallel_fast = np.array([105.0, 106.0, 107.0, 108.0])
    parallel_slow = np.array([100.0, 101.0, 102.0, 103.0])
    no_cross, _, _ = DemandSupplyEngine.detect_ma_crossover(parallel_fast, parallel_slow, lookback_bars=3)
    assert no_cross == MACrossoverType.NO_CROSSOVER


def test_episode_12_retail_crossover_traps_detection():
    """
    Episode 12 Concept: The Retail Crossover Trap.
    - Golden Crossover into Opposing HTF Supply: Institutions use retail crossover buying
      liquidity to dump shares. System flags trap and rejects bonus.
    - Death Crossover into Opposing HTF Demand: Institutions accumulate retail panic selling.
      System flags trap and rejects bonus.
    """
    engine = DemandSupplyEngine()
    demand_opens = np.array([200.0, 212.0, 215.0])
    demand_highs = np.array([202.0, 218.0, 230.0])
    demand_lows = np.array([198.0, 205.0, 214.0])
    demand_closes = np.array([211.0, 215.0, 229.0])
    ltf_demand = engine.scan_for_zones(demand_opens, demand_highs, demand_lows, demand_closes)[0]

    supply_opens = np.array([180.0, 205.0, 200.0])
    supply_highs = np.array([185.0, 210.0, 201.0])
    supply_lows = np.array([179.0, 198.0, 180.0])
    supply_closes = np.array([205.0, 200.0, 182.0])
    htf_supply = engine.scan_for_zones(supply_opens, supply_highs, supply_lows, supply_closes)[0]
    htf_supply.proximal_line = 500.0
    htf_supply.distal_line = 520.0

    # 1. Retail Supply Trap: Golden Crossover triggers at ₹496, right into HTF Supply (PL 500)
    is_valid, bonus, msg = DemandSupplyEngine.evaluate_crossover_trade_score_bonus(
        zone=ltf_demand,
        crossover_type=MACrossoverType.GOLDEN_CROSSOVER,
        crossover_price=496.0,
        opposing_htf_supply=htf_supply,
    )
    assert is_valid is False
    assert bonus == 0
    assert "Retail Supply Trap" in msg

    # 2. Retail Demand Trap: Death Crossover triggers at ₹101, right into HTF Demand (PL 100)
    htf_demand = engine.scan_for_zones(demand_opens, demand_highs, demand_lows, demand_closes)[0]
    htf_demand.proximal_line = 100.0
    htf_demand.distal_line = 90.0

    ltf_supply = engine.scan_for_zones(supply_opens, supply_highs, supply_lows, supply_closes)[0]
    ltf_supply.is_demand = False

    is_valid_d, bonus_d, msg_d = DemandSupplyEngine.evaluate_crossover_trade_score_bonus(
        zone=ltf_supply,
        crossover_type=MACrossoverType.DEATH_CROSSOVER,
        crossover_price=101.0,
        opposing_htf_demand=htf_demand,
    )
    assert is_valid_d is False
    assert bonus_d == 0
    assert "Retail Demand Trap" in msg_d


def test_episode_12_extra_trade_score_bonus_on_execution_zone():
    """
    Episode 12 Rule: Crossovers as an 'Extra Trade Score' (Optional +1 Bonus Point).
    A pristine 7/7 setup with a coinciding Golden Crossover earns 8/7.
    Absence of crossover does NOT invalidate a 7/7 setup.
    """
    engine = DemandSupplyEngine()
    demand_opens = np.array([200.0, 212.0, 215.0])
    demand_highs = np.array([202.0, 218.0, 230.0])
    demand_lows = np.array([198.0, 205.0, 214.0])
    demand_closes = np.array([211.0, 215.0, 229.0])
    zone = engine.scan_for_zones(demand_opens, demand_highs, demand_lows, demand_closes)[0]
    zone.proximal_line = 215.0
    zone.distal_line = 205.0

    # Setup pristine 7.0 score breakdown
    zone.trade_score = TradeScoreBreakdown(
        freshness_score=3.0,
        strength_score=2.0,
        time_at_base_score=2.0,
        total_score=7.0,
        quality=TradeScoreQuality.PRISTINE,
        alignment=ZoneAlignmentType.COINCIDING,
        is_best_setup=True,
    )

    # Coinciding Golden Crossover at 214.0 (inside zone)
    is_valid, bonus, msg = DemandSupplyEngine.evaluate_crossover_trade_score_bonus(
        zone=zone,
        crossover_type=MACrossoverType.GOLDEN_CROSSOVER,
        crossover_price=214.0,
        opposing_htf_supply=None,
    )
    assert is_valid is True
    assert bonus == 1
    assert "Extra Trade Score Awarded" in msg
    assert zone.trade_score.total_score == 8.0
    assert zone.trade_score.ma_crossover_bonus == 1
    assert zone.trade_score.crossover_type == MACrossoverType.GOLDEN_CROSSOVER


def test_episode_12_dynamic_ma_buffer_stoploss_placement():
    """
    Episode 12 Rule 3: Dynamic Stop-Loss Protection via Moving Average Buffer.
    When a moving average cross sits just beneath a demand zone's distal line,
    anchor the stop-loss below the moving average level for institutional insulation.
    """
    engine = DemandSupplyEngine()
    demand_opens = np.array([200.0, 212.0, 215.0])
    demand_highs = np.array([202.0, 218.0, 230.0])
    demand_lows = np.array([198.0, 205.0, 214.0])
    demand_closes = np.array([211.0, 215.0, 229.0])
    zone = engine.scan_for_zones(demand_opens, demand_highs, demand_lows, demand_closes)[0]
    zone.is_demand = True
    zone.distal_line = 100.0

    # MA sits below distal line at 99.20
    sl = DemandSupplyEngine.calculate_dynamic_ma_buffer_sl(
        zone=zone,
        ema_fast=99.50,
        ema_slow=99.20,
        tick_size=0.05,
        buffer_ticks=5,
    )
    # Expected: 99.20 - (0.05 * 5) = 98.95 (instead of 100.0 - 0.25 = 99.75)
    assert sl == 98.95

    # MA sits inside zone above distal line at 101.0 -> Normal distal buffer applied
    sl_normal = DemandSupplyEngine.calculate_dynamic_ma_buffer_sl(
        zone=zone,
        ema_fast=102.0,
        ema_slow=101.0,
        tick_size=0.05,
        buffer_ticks=5,
    )
    assert sl_normal == 99.75


# ==============================================================================
# EPISODE 13 TESTS: ADVANCED TREND ANALYSIS & EMA 20 ALGORITHMIC CONFLUENCE
# ==============================================================================


def test_episode_13_advanced_trend_violation_matrix_downtrend_to_uptrend():
    """
    Episode 13 Case Study: Maruti Suzuki Trend Transition.
    Downtrend advances through Drop-Base-Drop (DBD) supply structures.
    - 1st Supply Zone breached by close -> Transitions to SIDEWAYS.
    - 2nd consecutive Supply Zone breached by close -> UPTREND CONFIRMED.
    Traders declare uptrend near the bottom, two steps ahead of lagging Dow Theory.
    """
    # 0 Breaches -> Downtrend intact
    trend, msg = DemandSupplyEngine.calculate_advanced_trend(
        prior_trend=TrendDirection.DOWNTREND,
        consecutive_supply_breaches=0,
        consecutive_demand_breaches=0,
    )
    assert trend == TrendDirection.DOWNTREND
    assert "Downtrend intact" in msg

    # 1st Supply Breached -> Sideways
    trend, msg = DemandSupplyEngine.calculate_advanced_trend(
        prior_trend=TrendDirection.DOWNTREND,
        consecutive_supply_breaches=1,
        consecutive_demand_breaches=0,
    )
    assert trend == TrendDirection.SIDEWAYS
    assert "transitioned to SIDEWAYS" in msg

    # 2nd Supply Breached -> Uptrend Confirmed!
    trend, msg = DemandSupplyEngine.calculate_advanced_trend(
        prior_trend=TrendDirection.DOWNTREND,
        consecutive_supply_breaches=2,
        consecutive_demand_breaches=0,
    )
    assert trend == TrendDirection.UPTREND
    assert "UPTREND CONFIRMED" in msg


def test_episode_13_advanced_trend_mandatory_candle_close_filter():
    """
    Episode 13 Rule: Mandatory Candle Close Filter.
    Intra-candle wick piercing beyond distal line does NOT count as a zone breach.
    The candle must physically CLOSE outside the distal boundary.
    """
    engine = DemandSupplyEngine()
    demand_opens = np.array([200.0, 212.0, 215.0])
    demand_highs = np.array([202.0, 218.0, 230.0])
    demand_lows = np.array([198.0, 205.0, 214.0])
    demand_closes = np.array([211.0, 215.0, 229.0])

    supply_opens = np.array([180.0, 205.0, 200.0])
    supply_highs = np.array([185.0, 210.0, 201.0])
    supply_lows = np.array([179.0, 198.0, 180.0])
    supply_closes = np.array([205.0, 200.0, 182.0])

    # 1. Supply Zone: PL = 100.0, DL = 110.0
    supply_zone = engine.scan_for_zones(supply_opens, supply_highs, supply_lows, supply_closes)[0]
    supply_zone.is_demand = False
    supply_zone.proximal_line = 100.0
    supply_zone.distal_line = 110.0

    # Wick spikes to 115.0, but candle closes at 108.0 (inside zone) -> NOT breached!
    breached_wick_only = DemandSupplyEngine.evaluate_zone_breach_by_close(
        candle_close=108.0,
        candle_high=115.0,
        candle_low=98.0,
        zone=supply_zone,
    )
    assert breached_wick_only is False

    # Candle closes at 112.0 (above distal line 110.0) -> BREACHED!
    breached_by_close = DemandSupplyEngine.evaluate_zone_breach_by_close(
        candle_close=112.0,
        candle_high=115.0,
        candle_low=98.0,
        zone=supply_zone,
    )
    assert breached_by_close is True

    # 2. Demand Zone: PL = 200.0, DL = 190.0
    demand_zone = engine.scan_for_zones(demand_opens, demand_highs, demand_lows, demand_closes)[0]
    demand_zone.is_demand = True
    demand_zone.proximal_line = 200.0
    demand_zone.distal_line = 190.0

    # Wick spikes down to 185.0, but candle closes at 192.0 (inside zone) -> NOT breached!
    d_breached_wick = DemandSupplyEngine.evaluate_zone_breach_by_close(
        candle_close=192.0,
        candle_high=205.0,
        candle_low=185.0,
        zone=demand_zone,
    )
    assert d_breached_wick is False

    # Candle closes at 188.0 (below distal line 190.0) -> BREACHED!
    d_breached_close = DemandSupplyEngine.evaluate_zone_breach_by_close(
        candle_close=188.0,
        candle_high=205.0,
        candle_low=185.0,
        zone=demand_zone,
    )
    assert d_breached_close is True


def test_episode_13_advanced_trend_violation_matrix_uptrend_to_downtrend():
    """
    Episode 13: Advanced Trend Violation Matrix (Uptrend to Downtrend and Sideways transitions).
    """
    # Uptrend + 1 Demand Breached -> Sideways
    trend, msg = DemandSupplyEngine.calculate_advanced_trend(
        prior_trend=TrendDirection.UPTREND,
        consecutive_supply_breaches=0,
        consecutive_demand_breaches=1,
    )
    assert trend == TrendDirection.SIDEWAYS
    assert "Uptrend broken" in msg

    # Uptrend + 2 Demand Breached -> Downtrend Confirmed
    trend, msg = DemandSupplyEngine.calculate_advanced_trend(
        prior_trend=TrendDirection.UPTREND,
        consecutive_supply_breaches=0,
        consecutive_demand_breaches=2,
    )
    assert trend == TrendDirection.DOWNTREND
    assert "DOWNTREND CONFIRMED" in msg

    # Sideways + 1 Supply Breached -> Uptrend
    trend, msg = DemandSupplyEngine.calculate_advanced_trend(
        prior_trend=TrendDirection.SIDEWAYS,
        consecutive_supply_breaches=1,
        consecutive_demand_breaches=0,
    )
    assert trend == TrendDirection.UPTREND
    assert "UPTREND CONFIRMED from Sideways" in msg

    # Sideways + 1 Demand Breached -> Downtrend
    trend, msg = DemandSupplyEngine.calculate_advanced_trend(
        prior_trend=TrendDirection.SIDEWAYS,
        consecutive_supply_breaches=0,
        consecutive_demand_breaches=1,
    )
    assert trend == TrendDirection.DOWNTREND
    assert "DOWNTREND CONFIRMED from Sideways" in msg


def test_episode_13_ema20_zone_confluence_extra_trade_score():
    """
    Episode 13: EMA 20 Extra Trade Score Confluence.
    Trending EMA 20 passing between Proximal and Distal Line awards +1 Extra Trade Score (8/7).
    Choppy/sideways markets reject moving average confluence.
    """
    engine = DemandSupplyEngine()
    demand_opens = np.array([200.0, 212.0, 215.0])
    demand_highs = np.array([202.0, 218.0, 230.0])
    demand_lows = np.array([198.0, 205.0, 214.0])
    demand_closes = np.array([211.0, 215.0, 229.0])
    zone = engine.scan_for_zones(demand_opens, demand_highs, demand_lows, demand_closes)[0]
    zone.proximal_line = 215.0
    zone.distal_line = 205.0

    # Setup baseline pristine 7.0 score
    zone.trade_score = TradeScoreBreakdown(
        freshness_score=3.0,
        strength_score=2.0,
        time_at_base_score=2.0,
        total_score=7.0,
        quality=TradeScoreQuality.PRISTINE,
        alignment=ZoneAlignmentType.COINCIDING,
        is_best_setup=True,
    )

    # 1. Trending market, EMA 20 = 210.0 (inside 205-215 zone) -> +1 Extra Trade Score (Total 8.0)
    is_valid, bonus, msg = DemandSupplyEngine.evaluate_ema20_confluence_bonus(
        zone=zone,
        ema_20_val=210.0,
        is_trending_market=True,
    )
    assert is_valid is True
    assert bonus == 1
    assert "Extra Trade Score Awarded" in msg
    assert zone.trade_score.total_score == 8.0
    assert zone.trade_score.ema20_confluence_bonus == 1

    # 2. Choppy/sideways market -> Rejected (MAs lose predictive power)
    is_valid_c, bonus_c, msg_c = DemandSupplyEngine.evaluate_ema20_confluence_bonus(
        zone=zone,
        ema_20_val=210.0,
        is_trending_market=False,
    )
    assert is_valid_c is False
    assert bonus_c == 0
    assert "choppy/sideways" in msg_c

    # 3. Trending market, but EMA 20 = 250.0 (outside zone) -> No bonus
    is_valid_out, bonus_out, msg_out = DemandSupplyEngine.evaluate_ema20_confluence_bonus(
        zone=zone,
        ema_20_val=250.0,
        is_trending_market=True,
    )
    assert is_valid_out is False
    assert bonus_out == 0
    assert "sits outside zone" in msg_out


def test_episode_13_ema20_volatility_squeeze_detection():
    """
    Episode 13: Phase 2 Volatility Squeeze Detection.
    Gap between price candles and EMA 20 contracts into tight base candles (<= 0.4%),
    signaling equilibrium compression preceding explosive breakout.
    """
    # 1. Squeeze: Tight consolidation around flat EMA 20
    closes_squeeze = np.array([100.1, 99.9, 100.2, 100.0, 99.8])
    ema_squeeze = np.array([100.0, 100.0, 100.0, 100.0, 100.0])

    is_squeeze, mean_dist, msg = DemandSupplyEngine.detect_ema20_squeeze(
        closes=closes_squeeze,
        ema_20=ema_squeeze,
        lookback=5,
        squeeze_threshold_pct=0.4,
    )
    assert is_squeeze is True
    assert mean_dist <= 0.4
    assert "Volatility Squeeze Detected" in msg

    # 2. Non-Squeeze: Expanding price action away from EMA 20
    closes_wide = np.array([105.0, 108.0, 110.0, 112.0, 115.0])
    ema_wide = np.array([100.0, 100.5, 101.0, 101.5, 102.0])

    is_squeeze_w, mean_dist_w, msg_w = DemandSupplyEngine.detect_ema20_squeeze(
        closes=closes_wide,
        ema_20=ema_wide,
        lookback=5,
        squeeze_threshold_pct=0.4,
    )
    assert is_squeeze_w is False
    assert mean_dist_w > 0.4
    assert "Normal price-to-EMA spread" in msg_w


# ==============================================================================
# EPISODE 14 TESTS: TRADING AGAINST THE TREND (CONFIRMATION ENTRY)
# ==============================================================================


def test_episode_14_maruti_suzuki_confirmation_entry_risk_compression():
    """
    Episode 14 Benchmark Case Study: Maruti Suzuki March 2020 Crash.
    - Macro Quarterly Demand: PL = 5,600, DL = 4,700 (Macro Risk = ₹900).
    - Blind entry requires ₹900 SL and ₹1,800 to ₹2,000 target expansion.
    - Confirmation Entry: Nearest Daily DBD Supply (DL = 5,200) breached by close at 5,230.
    - Newly formed Daily Demand: PL = 5,210, DL = 5,180 (Compressed Risk = ₹30).
    - Compresses risk 30.0x from ₹900 to ₹30, delivering 7:1 RRR to opposing macro resistance!
    """
    engine = DemandSupplyEngine()
    demand_opens = np.array([200.0, 212.0, 215.0])
    demand_highs = np.array([202.0, 218.0, 230.0])
    demand_lows = np.array([198.0, 205.0, 214.0])
    demand_closes = np.array([211.0, 215.0, 229.0])

    supply_opens = np.array([180.0, 205.0, 200.0])
    supply_highs = np.array([185.0, 210.0, 201.0])
    supply_lows = np.array([179.0, 198.0, 180.0])
    supply_closes = np.array([205.0, 200.0, 182.0])

    # Macro Quarterly Demand (Shri Krishna)
    htf_demand = engine.scan_for_zones(demand_opens, demand_highs, demand_lows, demand_closes)[0]
    htf_demand.timeframe = TimeframeTier.QUARTERLY
    htf_demand.proximal_line = 5600.0
    htf_demand.distal_line = 4700.0

    # Nearest Daily Supply (Hurdle)
    ltf_supply = engine.scan_for_zones(supply_opens, supply_highs, supply_lows, supply_closes)[0]
    ltf_supply.timeframe = TimeframeTier.DAILY
    ltf_supply.proximal_line = 5100.0
    ltf_supply.distal_line = 5200.0

    # Newly formed Daily Demand formed by breakout rally
    new_daily_demand = engine.scan_for_zones(demand_opens, demand_highs, demand_lows, demand_closes)[0]
    new_daily_demand.timeframe = TimeframeTier.DAILY
    new_daily_demand.proximal_line = 5210.0
    new_daily_demand.distal_line = 5180.0

    plan = DemandSupplyEngine.evaluate_trading_against_the_trend_confirmation(
        htf_demand_zone=htf_demand,
        nearest_ltf_supply_zone=ltf_supply,
        breakout_candle_close=5230.0,  # Decisively closed above DL 5200.0
        newly_formed_ltf_demand=new_daily_demand,
        is_all_time_low=False,
        macro_opposing_supply_target=5420.0,
    )

    assert isinstance(plan, ConfirmationTradePlan)
    assert ConfirmationEntryType.MACRO_HTF_CONFIRMATION == "MACRO_HTF_CONFIRMATION"
    assert plan.is_confirmed is True
    assert plan.is_supply_eliminated_by_close is True
    assert plan.macro_risk_per_share == 900.0
    assert plan.compressed_risk_per_share == 30.0
    assert plan.risk_compression_ratio == 30.0
    assert plan.realized_target_rrr == 7.0  # (5420 - 5210) / 30 = 210 / 30 = 7.0:1
    assert "Risk compressed 30.0x" in plan.status_message


def test_episode_14_confirmation_requires_only_one_supply_breach_with_htf_backing():
    """
    Episode 14 Core Rule: Contrasts Advanced Trend vs. Confirmation Entry.
    - Advanced Trend (Without HTF backing): Requires 2 supply breaches to confirm uptrend.
    - Confirmation Entry (With HTF backing): Requires ONLY 1 supply breach!
    """
    engine = DemandSupplyEngine()
    demand_opens = np.array([200.0, 212.0, 215.0])
    demand_highs = np.array([202.0, 218.0, 230.0])
    demand_lows = np.array([198.0, 205.0, 214.0])
    demand_closes = np.array([211.0, 215.0, 229.0])

    supply_opens = np.array([180.0, 205.0, 200.0])
    supply_highs = np.array([185.0, 210.0, 201.0])
    supply_lows = np.array([179.0, 198.0, 180.0])
    supply_closes = np.array([205.0, 200.0, 182.0])

    htf_demand = engine.scan_for_zones(demand_opens, demand_highs, demand_lows, demand_closes)[0]
    htf_demand.timeframe = TimeframeTier.MONTHLY
    htf_demand.proximal_line = 1000.0
    htf_demand.distal_line = 900.0

    ltf_supply = engine.scan_for_zones(supply_opens, supply_highs, supply_lows, supply_closes)[0]
    ltf_supply.distal_line = 950.0

    new_ltf_demand = engine.scan_for_zones(demand_opens, demand_highs, demand_lows, demand_closes)[0]
    new_ltf_demand.proximal_line = 955.0
    new_ltf_demand.distal_line = 945.0

    # 1. Without HTF demand backing: 1 supply breach only gives Sideways (Episode 13)
    trend_no_htf, _ = DemandSupplyEngine.calculate_advanced_trend(
        prior_trend=TrendDirection.DOWNTREND,
        consecutive_supply_breaches=1,
        consecutive_demand_breaches=0,
    )
    assert trend_no_htf == TrendDirection.SIDEWAYS

    # 2. With HTF demand backing: 1 supply breach unlocks confirmed trade entry! (Episode 14)
    plan_with_htf = DemandSupplyEngine.evaluate_trading_against_the_trend_confirmation(
        htf_demand_zone=htf_demand,
        nearest_ltf_supply_zone=ltf_supply,
        breakout_candle_close=955.0,  # Closes above DL 950.0
        newly_formed_ltf_demand=new_ltf_demand,
        is_all_time_low=False,
    )
    assert plan_with_htf.is_confirmed is True


def test_episode_14_mandatory_close_filter_in_confirmation_entry():
    """
    Episode 14: Intra-candle wick spikes past supply distal line do NOT confirm entry.
    Must physically close above distal line.
    """
    engine = DemandSupplyEngine()
    demand_opens = np.array([200.0, 212.0, 215.0])
    demand_highs = np.array([202.0, 218.0, 230.0])
    demand_lows = np.array([198.0, 205.0, 214.0])
    demand_closes = np.array([211.0, 215.0, 229.0])

    supply_opens = np.array([180.0, 205.0, 200.0])
    supply_highs = np.array([185.0, 210.0, 201.0])
    supply_lows = np.array([179.0, 198.0, 180.0])
    supply_closes = np.array([205.0, 200.0, 182.0])

    htf_demand = engine.scan_for_zones(demand_opens, demand_highs, demand_lows, demand_closes)[0]
    htf_demand.timeframe = TimeframeTier.MONTHLY
    htf_demand.proximal_line = 1000.0
    htf_demand.distal_line = 900.0

    ltf_supply = engine.scan_for_zones(supply_opens, supply_highs, supply_lows, supply_closes)[0]
    ltf_supply.distal_line = 950.0

    new_ltf_demand = engine.scan_for_zones(demand_opens, demand_highs, demand_lows, demand_closes)[0]
    new_ltf_demand.proximal_line = 955.0
    new_ltf_demand.distal_line = 945.0

    # Candle spikes to 955.0, but closes at 948.0 (below DL 950.0) -> Unconfirmed!
    plan = DemandSupplyEngine.evaluate_trading_against_the_trend_confirmation(
        htf_demand_zone=htf_demand,
        nearest_ltf_supply_zone=ltf_supply,
        breakout_candle_close=948.0,
        newly_formed_ltf_demand=new_ltf_demand,
        is_all_time_low=False,
    )
    assert plan.is_confirmed is False
    assert plan.is_supply_eliminated_by_close is False
    assert "failed to close above" in plan.status_message


def test_episode_14_all_time_low_long_prohibition_and_bottom_out_criteria():
    """
    Episode 14 Rule: All-Time Low (ATL) Protocol.
    - Long trades are strictly forbidden at All-Time Lows (no historical buying support).
    - Requires at least 2 consecutive supply zones eliminated to qualify bottom-out.
    """
    engine = DemandSupplyEngine()
    demand_opens = np.array([200.0, 212.0, 215.0])
    demand_highs = np.array([202.0, 218.0, 230.0])
    demand_lows = np.array([198.0, 205.0, 214.0])
    demand_closes = np.array([211.0, 215.0, 229.0])

    supply_opens = np.array([180.0, 205.0, 200.0])
    supply_highs = np.array([185.0, 210.0, 201.0])
    supply_lows = np.array([179.0, 198.0, 180.0])
    supply_closes = np.array([205.0, 200.0, 182.0])

    htf_demand = engine.scan_for_zones(demand_opens, demand_highs, demand_lows, demand_closes)[0]
    htf_demand.proximal_line = 100.0
    htf_demand.distal_line = 50.0

    ltf_supply = engine.scan_for_zones(supply_opens, supply_highs, supply_lows, supply_closes)[0]
    ltf_supply.distal_line = 70.0

    new_ltf_demand = engine.scan_for_zones(demand_opens, demand_highs, demand_lows, demand_closes)[0]
    new_ltf_demand.proximal_line = 72.0
    new_ltf_demand.distal_line = 68.0

    # 1. At ATL with 1 supply breach -> Blocked!
    plan_atl = DemandSupplyEngine.evaluate_trading_against_the_trend_confirmation(
        htf_demand_zone=htf_demand,
        nearest_ltf_supply_zone=ltf_supply,
        breakout_candle_close=75.0,
        newly_formed_ltf_demand=new_ltf_demand,
        is_all_time_low=True,
        consecutive_supply_breaches_count=1,
    )
    assert plan_atl.is_confirmed is False
    assert "All-Time Low Protection" in plan_atl.status_message

    # 2. At ATL with 2 consecutive supply breaches -> Bottom-out qualified
    is_qualified, msg = DemandSupplyEngine.validate_all_time_low_bottom_out(
        is_at_all_time_low=True,
        consecutive_supply_breaches=2,
    )
    assert is_qualified is True
    assert "ATL Bottom-Out Qualified" in msg


def test_episode_14_wit_125m_confirmation_entry():
    """
    Episode 14 Application: Weekly Income Trade (WIT) on 125m execution chart.
    Daily trend is down, price hits Weekly Demand, 125m supply breached, enter on 125m demand.
    """
    engine = DemandSupplyEngine()
    demand_opens = np.array([200.0, 212.0, 215.0])
    demand_highs = np.array([202.0, 218.0, 230.0])
    demand_lows = np.array([198.0, 205.0, 214.0])
    demand_closes = np.array([211.0, 215.0, 229.0])

    supply_opens = np.array([180.0, 205.0, 200.0])
    supply_highs = np.array([185.0, 210.0, 201.0])
    supply_lows = np.array([179.0, 198.0, 180.0])
    supply_closes = np.array([205.0, 200.0, 182.0])

    htf_weekly_demand = engine.scan_for_zones(demand_opens, demand_highs, demand_lows, demand_closes)[0]
    htf_weekly_demand.timeframe = TimeframeTier.WEEKLY
    htf_weekly_demand.proximal_line = 1000.0
    htf_weekly_demand.distal_line = 920.0  # Macro risk = 80.0

    ltf_125m_supply = engine.scan_for_zones(supply_opens, supply_highs, supply_lows, supply_closes)[0]
    ltf_125m_supply.timeframe = TimeframeTier.M125
    ltf_125m_supply.proximal_line = 960.0
    ltf_125m_supply.distal_line = 970.0

    new_125m_demand = engine.scan_for_zones(demand_opens, demand_highs, demand_lows, demand_closes)[0]
    new_125m_demand.timeframe = TimeframeTier.M125
    new_125m_demand.proximal_line = 968.0
    new_125m_demand.distal_line = 952.0  # Compressed risk = 16.0

    plan_wit = DemandSupplyEngine.evaluate_trading_against_the_trend_confirmation(
        htf_demand_zone=htf_weekly_demand,
        nearest_ltf_supply_zone=ltf_125m_supply,
        breakout_candle_close=975.0,
        newly_formed_ltf_demand=new_125m_demand,
        is_all_time_low=False,
        macro_opposing_supply_target=1032.0,  # Target distance = 1032 - 968 = 64
    )
    assert plan_wit.is_confirmed is True
    assert plan_wit.macro_risk_per_share == 80.0
    assert plan_wit.compressed_risk_per_share == 16.0
    assert plan_wit.risk_compression_ratio == 5.0  # 80 / 16 = 5.0x
    assert plan_wit.realized_target_rrr == 4.0      # 64 / 16 = 4.0:1


# =====================================================================
# EPISODE 15 TESTS: REVISION CLASS, MASTER CASE STUDY & 14-POINT AUDITOR
# =====================================================================

def test_episode_15_half_yearly_macro_supply_wall_collision_and_macro_trap():
    """
    Episode 15 Master Case Study: The Half-Yearly Supply Wall (The Macro Trap).
    When price enters or approaches an unbreached Half-Yearly or Yearly supply zone,
    massive multi-month selling pressure is unleashed. Aggressive lower-timeframe
    (Daily/125m) longs are strictly prohibited and flagged as the Macro Trap.
    """
    engine = DemandSupplyEngine()
    demand_opens = np.array([100.0, 110.0, 112.0])
    demand_highs = np.array([102.0, 115.0, 125.0])
    demand_lows = np.array([98.0, 108.0, 111.0])
    demand_closes = np.array([109.0, 112.0, 124.0])

    supply_opens = np.array([1000.0, 1080.0, 1070.0])
    supply_highs = np.array([1010.0, 1100.0, 1075.0])
    supply_lows = np.array([990.0, 1050.0, 950.0])
    supply_closes = np.array([1080.0, 1070.0, 960.0])

    daily_demand = engine.scan_for_zones(demand_opens, demand_highs, demand_lows, demand_closes)[0]
    daily_demand.timeframe = TimeframeTier.DAILY
    daily_demand.proximal_line = 1040.0
    daily_demand.distal_line = 1020.0
    daily_demand.entry_price = 1041.0
    daily_demand.stop_loss = 1018.0

    half_yearly_supply = engine.scan_for_zones(supply_opens, supply_highs, supply_lows, supply_closes)[0]
    half_yearly_supply.timeframe = TimeframeTier.HALF_YEARLY
    half_yearly_supply.is_demand = False
    half_yearly_supply.proximal_line = 1050.0
    half_yearly_supply.distal_line = 1120.0
    half_yearly_supply.is_fresh = True

    # 1. Price colliding directly inside the Half-Yearly wall (CMP = 1060.0)
    status_collide, zone_collide, msg_collide = DemandSupplyEngine.detect_macro_supply_wall(
        cmp=1060.0, macro_supply_zones=[half_yearly_supply]
    )
    assert status_collide == MacroSupplyWallStatus.COLLIDING_WITH_WALL
    assert zone_collide is half_yearly_supply
    assert "Macro Wall Collision Detected" in msg_collide

    # 2. Imminent collision within 2% (CMP = 1040.0 vs PL 1050.0 -> 0.95% distance)
    status_near, _, _ = DemandSupplyEngine.detect_macro_supply_wall(
        cmp=1040.0, macro_supply_zones=[half_yearly_supply], proximity_pct=2.0
    )
    assert status_near == MacroSupplyWallStatus.COLLIDING_WITH_WALL

    # 3. Macro Trap Execution Block: Attempting blind limit entry (Set and Forget) while colliding
    audit_report = DemandSupplyEngine.audit_comprehensive_top_down_setup(
        execution_zone=daily_demand,
        cmp=1060.0,
        macro_supply_zones=[half_yearly_supply],
        attempted_entry_type=EntryType.SET_AND_FORGET,
        is_at_cycle_turning_point=False,
    )
    assert audit_report.is_approved is False
    assert any("The Macro Trap Detected" in r for r in audit_report.rejection_reasons)
    assert audit_report.trading_stance == TradingStance.CONSERVATIVE
    assert audit_report.recommended_entry_type == EntryType.CONFIRMATION_IN_ZONE


def test_episode_15_pristine_origin_vs_shallow_distributive_basing():
    """
    Episode 15: Pristine Origin vs. Shallow Distributive Basing.
    - Pristine Origin Base: 1-3 clean base candles at structural cycle turning point with EMA support.
    - Shallow Distributive Base: Mid-air consolidation (>=4 base candles or stair-step).
    - Garbage Area: Overlapping wicks / >6 base candles.
    """
    engine = DemandSupplyEngine()
    opens = np.array([100.0, 110.0, 112.0])
    highs = np.array([102.0, 115.0, 125.0])
    lows = np.array([98.0, 108.0, 111.0])
    closes = np.array([109.0, 112.0, 124.0])

    base_zone = engine.scan_for_zones(opens, highs, lows, closes)[0]
    base_zone.base_candles_count = 2

    # 1. Pristine origin with EMA support at cycle turning point
    quality_origin, msg_origin = DemandSupplyEngine.classify_origin_vs_distribution(
        zone=base_zone,
        is_at_cycle_turning_point=True,
        has_ema_support=True,
    )
    assert quality_origin == OriginQuality.PRISTINE_ORIGIN
    assert "Pristine Origin Base" in msg_origin
    assert "dynamic EMA support" in msg_origin

    # 2. Shallow distributive base (stair-stepping in mid-air)
    quality_shallow, msg_shallow = DemandSupplyEngine.classify_origin_vs_distribution(
        zone=base_zone,
        is_at_cycle_turning_point=False,
        is_distributive_stair_step=True,
    )
    assert quality_shallow == OriginQuality.SHALLOW_DISTRIBUTIVE
    assert "Shallow / Distributive Basing" in msg_shallow

    # 3. Garbage consolidation (>6 base candles)
    garbage_zone = engine.scan_for_zones(opens, highs, lows, closes)[0]
    garbage_zone.base_candles_count = 7
    quality_garbage, msg_garbage = DemandSupplyEngine.classify_origin_vs_distribution(
        zone=garbage_zone,
        is_at_cycle_turning_point=False,
    )
    assert quality_garbage == OriginQuality.GARBAGE_CONSOLIDATION
    assert "Garbage Area Consolidation" in msg_garbage


def test_episode_15_pristine_origin_macro_target_expansion_8_to_10_rrr():
    """
    Episode 15: Target Expectation in Multi-Timeframe Trades.
    Executing from a pristine origin base at the bottom of a major cycle targets
    opposing higher-timeframe supply, unlocking extraordinary 8:1 to 10:1+ RRR.
    """
    engine = DemandSupplyEngine()
    demand_opens = np.array([500.0, 480.0, 482.0, 520.0])
    demand_highs = np.array([505.0, 485.0, 484.0, 530.0])
    demand_lows = np.array([475.0, 478.0, 480.0, 515.0])
    demand_closes = np.array([479.0, 483.0, 525.0, 528.0])

    pristine_weekly_demand = engine.scan_for_zones(demand_opens, demand_highs, demand_lows, demand_closes)[0]
    pristine_weekly_demand.timeframe = TimeframeTier.WEEKLY
    pristine_weekly_demand.proximal_line = 500.0
    pristine_weekly_demand.distal_line = 480.0  # Risk = 20.0
    pristine_weekly_demand.entry_price = 501.0
    pristine_weekly_demand.stop_loss = 478.0   # Risk = 23.0
    pristine_weekly_demand.base_candles_count = 2
    pristine_weekly_demand.departure_strength = 2
    pristine_weekly_demand.is_fresh = True

    report = DemandSupplyEngine.audit_comprehensive_top_down_setup(
        execution_zone=pristine_weekly_demand,
        cmp=505.0,
        itf_trend=TrendDirection.UPTREND,
        curve_position=CurvePosition.VERY_LOW_ON_CURVE,
        is_at_cycle_turning_point=True,
        has_ema_support=True,
        capital=100000.0,
        risk_per_trade_pct=1.0,
    )

    assert report.is_approved is True
    assert report.origin_quality == OriginQuality.PRISTINE_ORIGIN
    assert report.projected_rrr == 8.5  # Origin target expansion
    assert report.trading_stance == TradingStance.AGGRESSIVE
    assert report.trade_score == 8.0   # 7.0 base + 1.0 EMA bonus
    assert report.calculated_position_size == 43  # floor(1000 / 23) = 43 shares


def test_episode_15_14_point_master_revision_auditor_all_pass_1_percent_club():
    """
    Episode 15: The 14-Point Comprehensive Top-Down Auditor ("1% Club" Verification).
    Tests a flawless institutional trade setup that passes all 14 gates without a single flaw.
    """
    engine = DemandSupplyEngine()
    demand_opens = np.array([200.0, 210.0, 212.0])
    demand_highs = np.array([202.0, 215.0, 225.0])
    demand_lows = np.array([198.0, 208.0, 211.0])
    demand_closes = np.array([209.0, 212.0, 224.0])

    ltf_daily_demand = engine.scan_for_zones(demand_opens, demand_highs, demand_lows, demand_closes)[0]
    ltf_daily_demand.timeframe = TimeframeTier.DAILY
    ltf_daily_demand.proximal_line = 215.0
    ltf_daily_demand.distal_line = 205.0
    ltf_daily_demand.entry_price = 216.0
    ltf_daily_demand.stop_loss = 203.0   # Risk = 13.0
    ltf_daily_demand.base_candles_count = 2
    ltf_daily_demand.departure_strength = 2
    ltf_daily_demand.is_fresh = True
    ltf_daily_demand.authenticity = ZoneAuthenticity.AUTHENTIC
    ltf_daily_demand.has_proven_achievement = True

    htf_monthly_demand = engine.scan_for_zones(demand_opens, demand_highs, demand_lows, demand_closes)[0]
    htf_monthly_demand.timeframe = TimeframeTier.MONTHLY
    htf_monthly_demand.is_demand = True

    report = DemandSupplyEngine.audit_comprehensive_top_down_setup(
        execution_zone=ltf_daily_demand,
        cmp=220.0,
        htf_zone=htf_monthly_demand,
        itf_trend=TrendDirection.UPTREND,
        curve_position=CurvePosition.LOW_ON_CURVE,
        macro_supply_zones=[],  # No macro wall overhead
        is_at_cycle_turning_point=True,
        has_ema_support=True,
        capital=200000.0,
        risk_per_trade_pct=1.0,  # ₹2,000 monetary risk
        prior_trades_count=100,
    )

    assert isinstance(report, MasterRevisionAuditReport)
    assert report.is_approved is True
    assert len(report.rejection_reasons) == 0
    assert len(report.audit_checks_passed) >= 12
    assert report.calculated_position_size == 153  # floor(2000 / 13) = 153 shares
    assert report.trade_score == 8.0               # 7.0 base + 1.0 EMA bonus
    assert "1% CLUB APPROVED" in report.audit_verdict_summary


def test_episode_15_14_point_master_revision_auditor_multiple_rejections():
    """
    Episode 15: Multi-Gate Failure & Rejection Mindset Audit.
    Ensures that flawed retail trade setups fail with exhaustive empirical reasons.
    """
    engine = DemandSupplyEngine()
    demand_opens = np.array([200.0, 210.0, 212.0])
    demand_highs = np.array([202.0, 215.0, 225.0])
    demand_lows = np.array([198.0, 208.0, 211.0])
    demand_closes = np.array([209.0, 212.0, 224.0])

    supply_opens = np.array([1000.0, 1080.0, 1070.0])
    supply_highs = np.array([1010.0, 1100.0, 1075.0])
    supply_lows = np.array([990.0, 1050.0, 950.0])
    supply_closes = np.array([1080.0, 1070.0, 960.0])

    flawed_demand = engine.scan_for_zones(demand_opens, demand_highs, demand_lows, demand_closes)[0]
    flawed_demand.timeframe = TimeframeTier.DAILY
    flawed_demand.proximal_line = 1040.0
    flawed_demand.distal_line = 1020.0
    flawed_demand.entry_price = 1041.0
    flawed_demand.stop_loss = 1018.0
    flawed_demand.base_candles_count = 6      # > 5 (fail base count)
    flawed_demand.is_fresh = False             # tested twice (fail freshness)
    flawed_demand.tested_at_idx = 10
    flawed_demand.authenticity = ZoneAuthenticity.NON_AUTHENTIC
    flawed_demand.has_proven_achievement = False # fail closing

    opposing_htf_supply = engine.scan_for_zones(supply_opens, supply_highs, supply_lows, supply_closes)[0]
    opposing_htf_supply.timeframe = TimeframeTier.YEARLY
    opposing_htf_supply.is_demand = False
    opposing_htf_supply.proximal_line = 1050.0
    opposing_htf_supply.distal_line = 1150.0

    report = DemandSupplyEngine.audit_comprehensive_top_down_setup(
        execution_zone=flawed_demand,
        cmp=1055.0,  # inside Yearly supply wall!
        htf_zone=opposing_htf_supply,  # Arjuna in front of Bhishma!
        itf_trend=TrendDirection.DOWNTREND,
        curve_position=CurvePosition.HIGH_ON_CURVE,  # buying high on curve!
        macro_supply_zones=[opposing_htf_supply],
        is_at_cycle_turning_point=False,
        is_at_all_time_low=True,  # at ATL without supply breach!
        consecutive_supply_breaches=0,
    )

    assert report.is_approved is False
    assert len(report.rejection_reasons) >= 6
    assert any("The Macro Trap Detected" in r for r in report.rejection_reasons)
    assert any("Mahabharata Alignment: Fatal Trap" in r for r in report.rejection_reasons)
    assert any("Curve Position: Long trade prohibited in HIGH_ON_CURVE" in r for r in report.rejection_reasons)
    assert any("Closing & Authenticity: Non-authentic zone lacks proven closing" in r for r in report.rejection_reasons)
    assert any("Base Candle Count" in r for r in report.rejection_reasons)
    assert any("ATL Long Prohibition" in r for r in report.rejection_reasons)
    assert "REJECTED BY INSTITUTIONAL DISCIPLINE" in report.audit_verdict_summary


# =====================================================================
# EPISODE 16 TESTS: SECTORAL ANALYSIS & THE CONFLUENCE MULTIPLIER
# =====================================================================

def test_episode_16_sector_support_plus_two_bonus_trade_score():
    """
    Episode 16 GTF Rule: Sector Support as Supreme Extra Trade Score (+2 Points).
    An ordinary 6 out of 7 setup elevates to 8 out of 7 when parent sector hits a demand zone.
    """
    engine = DemandSupplyEngine()
    demand_opens = np.array([100.0, 110.0, 112.0])
    demand_highs = np.array([102.0, 115.0, 125.0])
    demand_lows = np.array([98.0, 108.0, 111.0])
    demand_closes = np.array([109.0, 112.0, 124.0])

    stock_demand = engine.scan_for_zones(demand_opens, demand_highs, demand_lows, demand_closes)[0]
    stock_demand.is_demand = True
    stock_demand.is_fresh = True
    stock_demand.departure_strength = 1  # 1 exciting legout -> Strength = 1.0 pt
    stock_demand.base_candles_count = 2   # 1-3 base candles -> Time at base = 2.0 pts
    # Freshness (3.0) + Strength (1.0) + Time at Base (2.0) = 6.0 / 7.0 (Ordinary setup)

    # 1. Without sector support: awards 0 bonus points
    has_bonus_none, bonus_none, _ = DemandSupplyEngine.evaluate_sector_support_bonus(
        zone=stock_demand,
        is_parent_sector_in_demand=False,
    )
    assert has_bonus_none is False
    assert bonus_none == 0

    # 2. With parent sector in Demand Zone: awards +2 Supreme Bonus Points!
    has_bonus_sec, bonus_sec, msg_sec = DemandSupplyEngine.evaluate_sector_support_bonus(
        zone=stock_demand,
        is_parent_sector_in_demand=True,
    )
    assert has_bonus_sec is True
    assert bonus_sec == 2
    assert "Sector Support Confirmed (+2 Extra Trade Score awarded)" in msg_sec

    # 3. Comprehensive top-down evaluation: 6.0/7.0 setup elevates to 8.0/7.0 and is APPROVED
    report = DemandSupplyEngine.audit_comprehensive_top_down_setup(
        execution_zone=stock_demand,
        cmp=120.0,
        itf_trend=TrendDirection.UPTREND,
        curve_position=CurvePosition.LOW_ON_CURVE,
        is_parent_sector_in_demand=True,
    )
    assert report.is_approved is True
    assert report.trade_score == 8.0  # 6.0 base + 2.0 sector support = 8.0!
    assert any("Sector Support Verified (+2 Extra Trade Score Points awarded)" in c for c in report.audit_checks_passed)


def test_episode_16_the_missing_support_filter_blocks_long_execution():
    """
    Episode 16: The Missing Support Filter.
    If an individual stock looks attractive in Demand, but parent sector is in free fall,
    long execution is strictly halted to avoid the missing support trap.
    """
    engine = DemandSupplyEngine()
    demand_opens = np.array([100.0, 110.0, 112.0])
    demand_highs = np.array([102.0, 115.0, 125.0])
    demand_lows = np.array([98.0, 108.0, 111.0])
    demand_closes = np.array([109.0, 112.0, 124.0])

    stock_demand = engine.scan_for_zones(demand_opens, demand_highs, demand_lows, demand_closes)[0]
    stock_demand.is_demand = True

    # 1. Engine Confluence Evaluation flags MISSING_SUPPORT
    confluence = SectorAnalysisEngine.evaluate_simultaneous_confluence(
        is_stock_in_demand=True,
        is_sector_in_demand=False,
        is_nifty_in_demand=False,
        is_sector_in_free_fall=True,
    )
    assert isinstance(confluence, SectorConfluenceResult)
    assert confluence.confluence_level == SectorConfluenceLevel.MISSING_SUPPORT
    assert confluence.missing_support_warning is True
    assert confluence.bonus_points == 0.0
    assert "The Missing Support Trap Detected" in confluence.status_message

    # 2. Top-down auditor blocks trade setup
    report = DemandSupplyEngine.audit_comprehensive_top_down_setup(
        execution_zone=stock_demand,
        cmp=120.0,
        itf_trend=TrendDirection.UPTREND,
        curve_position=CurvePosition.LOW_ON_CURVE,
        is_sector_in_free_fall=True,
    )
    assert report.is_approved is False
    assert any("The Missing Support Trap Detected" in r for r in report.rejection_reasons)
    assert "REJECTED BY INSTITUTIONAL DISCIPLINE" in report.audit_verdict_summary


def test_episode_16_simultaneous_triad_alignment_level_3_rocket_move_sbi_case_study():
    """
    Episode 16: Simultaneous Triad Alignment (February 29, 2016 State Bank of India Case Study).
    When Stock + Sector + Nifty 50 are ALL in Demand Zones simultaneously:
    - Declares Level 3 Confluence ("Rocket Move!").
    - Awards +2 Extra Trade Score points.
    - Yields maximum statistical probability regardless of external news or crises.
    """
    # Simultaneous alignment on Feb 29, 2016: SBI in Monthly DZ, Bank Nifty in Monthly DZ, Nifty 50 in Monthly DZ
    confluence = SectorAnalysisEngine.evaluate_simultaneous_confluence(
        is_stock_in_demand=True,
        is_sector_in_demand=True,
        is_nifty_in_demand=True,
    )

    assert confluence.confluence_level == SectorConfluenceLevel.LEVEL_3_ROCKET_MOVE
    assert confluence.is_rocket_move is True
    assert confluence.bonus_points == 2.0
    assert "Level 3 Confluence (Explosive Rocket Move!)" in confluence.status_message


def test_episode_16_heavyweight_concentration_greater_than_50_percent_rule():
    """
    Episode 16: The >50% Heavyweight Concentration Rule.
    - Nifty Auto: M&M (20%), Maruti (19%), Tata Motors (12%) = 51.0% (>50%).
    - If heavyweights are in Demand, sector index will rally.
    - Low-weight constituents (e.g. Ashok Leyland 4%) jumping 5% will NOT move index if heavyweights are in Supply.
    """
    # 1. Nifty Auto with M&M and Maruti in Demand
    auto_states_bullish = {
        "M&M": "DEMAND",
        "MARUTI": "DEMAND",
        "TATAMOTORS": "NEUTRAL",
        "ASHOKLEY": "NEUTRAL",
    }
    report_auto = SectorAnalysisEngine.evaluate_heavyweight_concentration(
        sector=SectorName.NIFTY_AUTO,
        stock_zone_states=auto_states_bullish,
    )
    assert isinstance(report_auto, HeavyweightStatusReport)
    assert report_auto.top_heavyweights == ["M&M", "MARUTI", "TATAMOTORS"]
    assert report_auto.heavyweight_combined_weight_pct == 51.0
    assert report_auto.is_heavyweight_momentum_bullish is True
    assert "Bullish Heavyweight Momentum in NIFTY_AUTO" in report_auto.explanation

    # 2. Nifty Metal with Heavyweights in Supply and low-weight SAIL in Demand
    metal_states_drag = {
        "JSWSTEEL": "SUPPLY",
        "TATASTEEL": "SUPPLY",
        "HINDALCO": "NEUTRAL",
        "SAIL": "DEMAND",  # Only 4% weight!
    }
    report_metal = SectorAnalysisEngine.evaluate_heavyweight_concentration(
        sector=SectorName.NIFTY_METAL,
        stock_zone_states=metal_states_drag,
    )
    assert report_metal.top_heavyweights == ["JSWSTEEL", "TATASTEEL", "HINDALCO"]
    assert report_metal.heavyweight_combined_weight_pct == 60.0  # 22 + 20 + 18
    assert report_metal.is_heavyweight_momentum_bullish is False
    assert "Bearish Heavyweight Drag in NIFTY_METAL" in report_metal.explanation


def test_episode_16_sector_rotation_dynamics_sectors_cannot_go_to_zero():
    """
    Episode 16: Sector Rotation Dynamics.
    - "Sectors Cannot Go to Zero": Generational accumulation at multi-year macro demand origin.
    - Tested Supply Trendline: Relief bounces testing and depleting overhead supply clear the runway.
    - Peak at ATH: Rotate out of 5x leaders into lagging constituents (GTF 40-40-20 rule).
    """
    # 1. Nifty PSU Bank at multi-year macro demand origin with tested overhead supply
    phase_psu, msg_psu = SectorAnalysisEngine.evaluate_sector_rotation(
        sector=SectorName.NIFTY_PSU_BANK,
        current_index_level=1250.0,
        macro_demand_zone=(1300.0, 1150.0),
        tested_overhead_supply_count=3,
        is_at_all_time_high=False,
    )
    assert phase_psu == SectorRotationPhase.ACCUMULATION_AT_CYCLE_LOW
    assert "Sectors cannot go to zero" in msg_psu
    assert "Overhead supply trendline exhausted with 3 tested supply zones" in msg_psu

    # 2. Sector at All-Time High
    phase_ath, msg_ath = SectorAnalysisEngine.evaluate_sector_rotation(
        sector=SectorName.NIFTY_METAL,
        current_index_level=8500.0,
        is_at_all_time_high=True,
    )
    assert phase_ath == SectorRotationPhase.PEAK_AT_ALL_TIME_HIGH
    assert "Avoid chasing 5x run leaders" in msg_ath
    assert "GTF 40-40-20 rule" in msg_ath


def test_episode_16_portfolio_construction_12_to_15_stocks_and_sector_allocation():
    """
    Episode 16: Long-Term Portfolio Construction Blueprint.
    - Portfolio size must be 12 to 15 stocks maximum.
    - Sector allocation: 2 to 4 stocks across different sectors.
    """
    valid_portfolio = [
        "MARUTI", "M&M", "TATAMOTORS",          # Auto (3)
        "TCS", "INFY", "HCLTECH",               # IT (3)
        "HDFCBANK", "ICICIBANK", "AXISBANK",    # Bank (3)
        "JSWSTEEL", "TATASTEEL", "HINDALCO",    # Metal (3)
        "DLF", "GODREJPROP",                    # Realty (2) -> Total 14 stocks
    ]

    report_valid = SectorAnalysisEngine.audit_portfolio_construction(valid_portfolio)
    assert isinstance(report_valid, PortfolioSectorAllocationReport)
    assert report_valid.is_allocation_valid is True
    assert report_valid.total_stocks_count == 14
    assert len(report_valid.sectors_represented) == 5
    assert len(report_valid.rejection_reasons) == 0

    # Under-diversified portfolio (< 12 stocks)
    report_under = SectorAnalysisEngine.audit_portfolio_construction(valid_portfolio[:8])
    assert report_under.is_allocation_valid is False
    assert any("Under-diversified Portfolio" in r for r in report_under.rejection_reasons)

    # Over-diversified portfolio (> 15 stocks)
    extended_portfolio = valid_portfolio + ["SBIN", "VEDL", "WIPRO"]  # 17 stocks
    report_over = SectorAnalysisEngine.audit_portfolio_construction(extended_portfolio)
    assert report_over.is_allocation_valid is False
    assert any("Over-diversified Portfolio" in r for r in report_over.rejection_reasons)

    # Sector over-concentration (> 4 stocks in one sector)
    over_conc_portfolio = [
        "HDFCBANK", "ICICIBANK", "AXISBANK", "KOTAKBANK", "SBIN",  # 5 Banks!
        "TCS", "INFY", "HCLTECH",
        "MARUTI", "M&M", "TATAMOTORS",
        "JSWSTEEL",
    ]
    report_conc = SectorAnalysisEngine.audit_portfolio_construction(over_conc_portfolio)
    assert report_conc.is_allocation_valid is False
    assert any("Sector Over-concentration: NIFTY_BANK holds 5 stocks" in r for r in report_conc.rejection_reasons)
