"""
Demand & Supply Core Engine (Trading in the Zone / GTF Methodology).
Codifies institutional order-matching mechanics, Exciting vs Base candle classification,
structural zone detection (DBR, RBR, RBD, DBD), exact Zone Marking (Proximal & Distal lines),
and Freshness vs. Tested evaluation.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple
import numpy as np


class CandleType(str, Enum):
    GREEN_EXCITING = "GREEN_EXCITING"  # Demand > Supply (Body >= 50% of Range)
    RED_EXCITING = "RED_EXCITING"      # Supply > Demand (Body >= 50% of Range)
    BASE = "BASE"                      # Equilibrium / Tug-of-War (Body < 50% of Range)


class ZoneType(str, Enum):
    DEMAND_DBR = "DEMAND_DBR"  # Drop - Base - Rally (Reversal Demand)
    DEMAND_RBR = "DEMAND_RBR"  # Rally - Base - Rally (Continuation Demand)
    SUPPLY_RBD = "SUPPLY_RBD"  # Rally - Base - Drop (Reversal Supply)
    SUPPLY_DBD = "SUPPLY_DBD"  # Drop - Base - Drop (Continuation Supply)


@dataclass
class CandleFeature:
    index: int
    open: float
    high: float
    low: float
    close: float
    range: float
    body: float
    body_ratio: float
    candle_type: CandleType


@dataclass
class IdentifiedZone:
    zone_type: ZoneType
    is_demand: bool
    is_reversal: bool
    base_start_idx: int
    base_end_idx: int
    base_candles_count: int
    first_leg_out_idx: int
    
    # Exact Zone Marking (Episode 3 Formulas)
    proximal_line: float       # Entry Reference
    distal_line: float         # Stop-Loss Reference
    zone_width: float          # Inherent risk per share (Proximal - Distal)
    
    departure_strength: int    # Consecutive exciting candles leaving the zone
    departure_velocity: float  # Total price expansion in leg-out
    
    is_fresh: bool             # True if price has NEVER touched proximal line since leg-out
    tested_at_idx: Optional[int] = None
    is_high_quality: bool = True


class DemandSupplyEngine:
    """
    Core Price Action Engine trained on Institutional Order Flow and Demand-Supply Imbalances.
    """

    def __init__(self, min_range_atr_ratio: float = 0.25, max_base_candles: int = 6):
        self.min_range_atr_ratio = min_range_atr_ratio
        self.max_base_candles = max_base_candles

    def classify_candle(
        self,
        index: int,
        open_p: float,
        high_p: float,
        low_p: float,
        close_p: float,
        atr14: float = 0.0,
    ) -> CandleFeature:
        """
        Classifies a single candlestick using GTF 50% body-to-range rule.
        """
        total_range = high_p - low_p
        if total_range <= 1e-6:
            return CandleFeature(
                index, open_p, high_p, low_p, close_p, 0.0, 0.0, 0.0, CandleType.BASE
            )

        body = abs(close_p - open_p)
        body_ratio = body / total_range

        # Filter out micro-range candles that have no meaningful price discovery
        is_meaningful = True
        if atr14 > 0 and total_range < (self.min_range_atr_ratio * atr14):
            is_meaningful = False

        if body_ratio >= 0.50 and is_meaningful:
            c_type = CandleType.GREEN_EXCITING if close_p > open_p else CandleType.RED_EXCITING
        else:
            c_type = CandleType.BASE

        return CandleFeature(
            index=index,
            open=open_p,
            high=high_p,
            low=low_p,
            close=close_p,
            range=round(total_range, 2),
            body=round(body, 2),
            body_ratio=round(body_ratio, 3),
            candle_type=c_type,
        )

    def scan_for_zones(
        self,
        opens: np.ndarray,
        highs: np.ndarray,
        lows: np.ndarray,
        closes: np.ndarray,
        atr14: Optional[np.ndarray] = None,
    ) -> List[IdentifiedZone]:
        """
        Scans series of candles to identify institutional Demand and Supply zones:
        Leg-in (Arrival) -> Base Candles (Pending Orders) -> Leg-out (Departure).
        Computes Proximal Line, Distal Line, and verifies Freshness.
        """
        n = len(closes)
        if n < 3:
            return []

        # 1. Classify all candles
        classified: List[CandleFeature] = []
        for i in range(n):
            a = float(atr14[i]) if atr14 is not None and i < len(atr14) else 0.0
            classified.append(
                self.classify_candle(i, opens[i], highs[i], lows[i], closes[i], a)
            )

        zones: List[IdentifiedZone] = []

        # 2. Pattern recognition for zones
        i = 1
        while i < n - 1:
            leg_in = classified[i - 1]
            if leg_in.candle_type == CandleType.BASE:
                i += 1
                continue

            # Check if current is BASE
            if classified[i].candle_type == CandleType.BASE:
                base_start = i
                while i < n and classified[i].candle_type == CandleType.BASE:
                    i += 1
                base_end = i - 1
                base_count = base_end - base_start + 1

                # Check leg-out candle(s)
                if i < n and classified[i].candle_type != CandleType.BASE:
                    leg_out = classified[i]
                    first_leg_out_idx = i

                    # Count consecutive exciting candles in leg-out
                    departure_strength = 0
                    dep_idx = i
                    departure_p_start = leg_out.open
                    departure_p_end = leg_out.close

                    while dep_idx < n and classified[dep_idx].candle_type == leg_out.candle_type:
                        departure_strength += 1
                        departure_p_end = classified[dep_idx].close
                        dep_idx += 1

                    dep_velocity = abs(departure_p_end - departure_p_start)
                    is_hq = (1 <= base_count <= self.max_base_candles) and (departure_strength >= 1)

                    # Determine zone type
                    z_type = None
                    is_demand = False
                    is_reversal = False

                    if leg_in.candle_type == CandleType.RED_EXCITING and leg_out.candle_type == CandleType.GREEN_EXCITING:
                        z_type = ZoneType.DEMAND_DBR
                        is_demand = True
                        is_reversal = True
                    elif leg_in.candle_type == CandleType.GREEN_EXCITING and leg_out.candle_type == CandleType.GREEN_EXCITING:
                        z_type = ZoneType.DEMAND_RBR
                        is_demand = True
                        is_reversal = False
                    elif leg_in.candle_type == CandleType.GREEN_EXCITING and leg_out.candle_type == CandleType.RED_EXCITING:
                        z_type = ZoneType.SUPPLY_RBD
                        is_demand = False
                        is_reversal = True
                    elif leg_in.candle_type == CandleType.RED_EXCITING and leg_out.candle_type == CandleType.RED_EXCITING:
                        z_type = ZoneType.SUPPLY_DBD
                        is_demand = False
                        is_reversal = False

                    if z_type:
                        # 3. Exact Zone Marking (Episode 3 Formulas)
                        base_candles = classified[base_start : base_end + 1]

                        if is_demand:
                            # Demand: Proximal = Highest Body of all base candles
                            proximal = max(max(b.open, b.close) for b in base_candles)
                            # Demand: Distal = Lowest Wick of all base candles
                            distal = min(b.low for b in base_candles)
                            zone_width = round(proximal - distal, 2)
                        else:
                            # Supply: Proximal = Lowest Body of all base candles
                            proximal = min(min(b.open, b.close) for b in base_candles)
                            # Supply: Distal = Highest Wick of all base candles
                            distal = max(b.high for b in base_candles)
                            zone_width = round(distal - proximal, 2)

                        # 4. Freshness vs Tested Evaluation
                        # Monitored immediately after the first leg-out candle
                        is_fresh = True
                        tested_at = None

                        for k in range(first_leg_out_idx + 1, n):
                            if is_demand:
                                # In Demand: If low touches or pierces Proximal line
                                if lows[k] <= proximal:
                                    is_fresh = False
                                    tested_at = k
                                    break
                            else:
                                # In Supply: If high touches or pierces Proximal line
                                if highs[k] >= proximal:
                                    is_fresh = False
                                    tested_at = k
                                    break

                        zones.append(
                            IdentifiedZone(
                                zone_type=z_type,
                                is_demand=is_demand,
                                is_reversal=is_reversal,
                                base_start_idx=base_start,
                                base_end_idx=base_end,
                                base_candles_count=base_count,
                                first_leg_out_idx=first_leg_out_idx,
                                proximal_line=round(proximal, 2),
                                distal_line=round(distal, 2),
                                zone_width=zone_width,
                                departure_strength=departure_strength,
                                departure_velocity=round(dep_velocity, 2),
                                is_fresh=is_fresh,
                                tested_at_idx=tested_at,
                                is_high_quality=is_hq,
                            )
                        )
            else:
                i += 1

        return zones

    def find_active_trade_zones(
        self,
        cmp: float,
        opens: np.ndarray,
        highs: np.ndarray,
        lows: np.ndarray,
        closes: np.ndarray,
        only_fresh: bool = True,
    ) -> Tuple[List[IdentifiedZone], List[IdentifiedZone]]:
        """
        Navigates relative to Current Market Price (CMP) as taught in Episode 3:
        1. Demand Zones: Look Left & Down (Proximal Line < CMP).
        2. Supply Zones: Look Left & Up (Proximal Line > CMP).
        """
        all_zones = self.scan_for_zones(opens, highs, lows, closes)

        demand_zones: List[IdentifiedZone] = []
        supply_zones: List[IdentifiedZone] = []

        for z in all_zones:
            if only_fresh and not z.is_fresh:
                continue

            if z.is_demand and z.proximal_line < cmp:
                demand_zones.append(z)
            elif not z.is_demand and z.proximal_line > cmp:
                supply_zones.append(z)

        # Sort Demand descending by proximal line (closest discounted zone below CMP first)
        demand_zones.sort(key=lambda x: x.proximal_line, reverse=True)

        # Sort Supply ascending by proximal line (closest premium zone above CMP first)
        supply_zones.sort(key=lambda x: x.proximal_line)

        return demand_zones, supply_zones
