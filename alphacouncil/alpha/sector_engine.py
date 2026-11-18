"""
Sectoral Analysis Core Engine (Trading in the Zone / GTF Methodology).
Codifies Episode 16 principles:
1. The +2 Extra Trade Score for Sector Support (The Supreme Add-on).
2. Nifty 50 as the Universal Umbrella Benchmark.
3. Sector Weightings & Heavyweight Concentration (>50% Rule).
4. Simultaneous Zone Alignment (The Confluence Multiplier / Rocket Move):
   - Level 1: Only Nifty in Demand Zone (+0.5 modest push).
   - Level 2: Only Stock in Demand Zone (+0.0 independent bounce).
   - Level 3: Stock + Sector + Nifty ALL in Demand Zones simultaneously (+2.0 Rocket Move!).
5. The Missing Support Filter (Blocks longs when sector is in free fall).
6. Sector Rotation Dynamics & "Sectors Cannot Go to Zero" Axiom.
7. Portfolio Construction Rules (12-15 stocks max, 2-4 per sector, 40-40-20 rule).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class SectorName(str, Enum):
    NIFTY_50 = "NIFTY_50"
    NIFTY_BANK = "NIFTY_BANK"
    NIFTY_FIN_SERVICES = "NIFTY_FIN_SERVICES"
    NIFTY_AUTO = "NIFTY_AUTO"
    NIFTY_IT = "NIFTY_IT"
    NIFTY_METAL = "NIFTY_METAL"
    NIFTY_REALTY = "NIFTY_REALTY"
    NIFTY_PHARMA = "NIFTY_PHARMA"
    NIFTY_FMCG = "NIFTY_FMCG"
    NIFTY_ENERGY = "NIFTY_ENERGY"
    NIFTY_PSU_BANK = "NIFTY_PSU_BANK"
    NIFTY_PVT_BANK = "NIFTY_PVT_BANK"
    NIFTY_MEDIA = "NIFTY_MEDIA"
    NIFTY_INFRA = "NIFTY_INFRA"


class SectorConfluenceLevel(str, Enum):
    LEVEL_1_NIFTY_ONLY = "LEVEL_1_NIFTY_ONLY"    # Modest macro push (+0.5)
    LEVEL_2_STOCK_ONLY = "LEVEL_2_STOCK_ONLY"    # Stock bounces independently (+0.0)
    LEVEL_3_ROCKET_MOVE = "LEVEL_3_ROCKET_MOVE"  # Stock + Sector + Nifty ALL in Demand (+2.0 Rocket Move)
    SECTOR_SUPPORTED = "SECTOR_SUPPORTED"        # Stock + Sector in Demand (+2.0)
    MISSING_SUPPORT = "MISSING_SUPPORT"          # Stock in Demand, but Sector in free fall (Veto/Halt)


class SectorRotationPhase(str, Enum):
    ACCUMULATION_AT_CYCLE_LOW = "ACCUMULATION_AT_CYCLE_LOW"  # Multi-year low / macro origin (Sectors Cannot Go to Zero)
    EARLY_EXPANSION = "EARLY_EXPANSION"                      # Breakout from base through tested supply trendline
    PEAK_AT_ALL_TIME_HIGH = "PEAK_AT_ALL_TIME_HIGH"          # Distribution at ATH; rotate to lagging constituents
    DISTRIBUTION_AT_SUPPLY = "DISTRIBUTION_AT_SUPPLY"        # Multi-month selling pressure from macro supply
    CORRECTION_WITH_TESTED_SUPPLY = "CORRECTION_WITH_TESTED_SUPPLY" # Relief rallies testing and consuming supply


# =====================================================================
# OFFICIAL NSE SECTOR WEIGHTINGS REGISTRY (FACT SHEET GROUNDING)
# =====================================================================

NSE_SECTOR_WEIGHTINGS: Dict[SectorName, Dict[str, float]] = {
    SectorName.NIFTY_AUTO: {
        "M&M": 20.0,
        "MARUTI": 19.0,
        "TATAMOTORS": 12.0,  # Top 3 account for 51.0% (>50%)
        "BAJAJ-AUTO": 9.0,
        "EICHERMOT": 7.0,
        "HEROMOTOCO": 6.0,
        "TVSMOTOR": 5.0,
        "BHARATFORG": 4.0,
        "ASHOKLEY": 4.0,
        "BALKRISIND": 3.0,
        "MOTHERSON": 3.0,
        "BOSCHLTD": 2.5,
        "APOLLOTYRE": 2.0,
        "MRF": 1.5,
        "TIINDIA": 1.0,
    },
    SectorName.NIFTY_IT: {
        "TCS": 28.0,
        "INFY": 26.0,  # Top 2 account for 54.0% (>50%)
        "HCLTECH": 10.0,
        "WIPRO": 8.0,
        "TECHM": 7.0,
        "LTIM": 6.0,
        "PERSISTENT": 5.0,
        "COFORGE": 4.0,
        "MPHASIS": 3.0,
        "LTTS": 3.0,
    },
    SectorName.NIFTY_FIN_SERVICES: {
        "HDFCBANK": 29.0,
        "ICICIBANK": 22.0,  # Top 2 account for 51.0% (>50%)
        "KOTAKBANK": 10.0,
        "AXISBANK": 10.0,
        "SBIN": 9.0,
        "BAJFINANCE": 8.0,
        "BAJAJFINSV": 4.0,
        "CHOLAFIN": 3.0,
        "SHRIRAMFIN": 2.5,
        "HDFCLIFE": 2.5,
    },
    SectorName.NIFTY_BANK: {
        "HDFCBANK": 29.0,
        "ICICIBANK": 23.0,  # Top 2 account for 52.0% (>50%)
        "AXISBANK": 11.0,
        "KOTAKBANK": 10.0,
        "SBIN": 9.0,
        "INDUSINDBK": 6.0,
        "BANKBARODA": 3.5,
        "PNB": 2.5,
        "CANBK": 2.0,
        "FEDERALBNK": 1.5,
        "IDFCFIRSTB": 1.5,
        "AUBANK": 1.0,
    },
    SectorName.NIFTY_METAL: {
        "JSWSTEEL": 22.0,
        "TATASTEEL": 20.0,
        "HINDALCO": 18.0,  # Top 3 account for 60.0% (>50%)
        "ADANIENT": 15.0,
        "VEDL": 8.0,
        "JINDALSTEL": 6.0,
        "SAIL": 4.0,
        "NATIONALUM": 3.0,
        "NMDC": 2.5,
        "HINDZINC": 1.5,
    },
    SectorName.NIFTY_REALTY: {
        "DLF": 30.0,
        "GODREJPROP": 20.0,  # Top 2 account for 50.0%
        "OBEROIRLTY": 15.0,
        "PHOENIXLTD": 11.0,
        "PRESTIGE": 9.0,
        "BRIGADE": 5.0,
        "SOBHA": 4.0,
        "MAHLIFE": 3.0,
        "SUNTECK": 2.0,
        "IBREALEST": 1.0,
    },
    SectorName.NIFTY_PSU_BANK: {
        "SBIN": 38.0,
        "BANKBARODA": 16.0,  # Top 2 account for 54.0%
        "PNB": 14.0,
        "CANBK": 12.0,
        "UNIONBANK": 7.0,
        "INDIANB": 5.0,
        "BANKINDIA": 3.0,
        "CENTRALBK": 2.0,
        "IOB": 1.5,
        "UCOBANK": 1.5,
    },
}

# Reverse lookup mapping from ticker symbol to primary SectorName
STOCK_TO_SECTOR_LOOKUP: Dict[str, SectorName] = {
    # Auto
    "M&M": SectorName.NIFTY_AUTO,
    "MARUTI": SectorName.NIFTY_AUTO,
    "TATAMOTORS": SectorName.NIFTY_AUTO,
    "BAJAJ-AUTO": SectorName.NIFTY_AUTO,
    "EICHERMOT": SectorName.NIFTY_AUTO,
    "HEROMOTOCO": SectorName.NIFTY_AUTO,
    "TVSMOTOR": SectorName.NIFTY_AUTO,
    "ASHOKLEY": SectorName.NIFTY_AUTO,
    "BALKRISIND": SectorName.NIFTY_AUTO,
    # IT
    "TCS": SectorName.NIFTY_IT,
    "INFY": SectorName.NIFTY_IT,
    "HCLTECH": SectorName.NIFTY_IT,
    "WIPRO": SectorName.NIFTY_IT,
    "TECHM": SectorName.NIFTY_IT,
    "LTIM": SectorName.NIFTY_IT,
    # Banking & Finance
    "HDFCBANK": SectorName.NIFTY_BANK,
    "ICICIBANK": SectorName.NIFTY_BANK,
    "AXISBANK": SectorName.NIFTY_BANK,
    "KOTAKBANK": SectorName.NIFTY_BANK,
    "SBIN": SectorName.NIFTY_BANK,
    "BANKBARODA": SectorName.NIFTY_BANK,
    "CANBK": SectorName.NIFTY_BANK,
    "BAJFINANCE": SectorName.NIFTY_FIN_SERVICES,
    "BAJAJFINSV": SectorName.NIFTY_FIN_SERVICES,
    # Metal
    "JSWSTEEL": SectorName.NIFTY_METAL,
    "TATASTEEL": SectorName.NIFTY_METAL,
    "HINDALCO": SectorName.NIFTY_METAL,
    "ADANIENT": SectorName.NIFTY_METAL,
    "VEDL": SectorName.NIFTY_METAL,
    "SAIL": SectorName.NIFTY_METAL,
    "NATIONALUM": SectorName.NIFTY_METAL,
    # Realty
    "DLF": SectorName.NIFTY_REALTY,
    "GODREJPROP": SectorName.NIFTY_REALTY,
    "OBEROIRLTY": SectorName.NIFTY_REALTY,
}


@dataclass
class SectorConfluenceResult:
    confluence_level: SectorConfluenceLevel
    is_stock_in_demand: bool
    is_sector_in_demand: bool
    is_nifty_in_demand: bool
    bonus_points: float
    is_rocket_move: bool
    missing_support_warning: bool
    status_message: str


@dataclass
class HeavyweightStatusReport:
    sector: SectorName
    top_heavyweights: List[str]
    heavyweight_combined_weight_pct: float
    heavyweights_in_demand: List[str]
    heavyweights_in_supply: List[str]
    is_heavyweight_momentum_bullish: bool
    explanation: str


@dataclass
class PortfolioSectorAllocationReport:
    is_allocation_valid: bool
    total_stocks_count: int
    sectors_represented: List[SectorName]
    stocks_per_sector: Dict[str, int]
    rotation_arbitrage_candidates: List[str] = field(default_factory=list)
    rejection_reasons: List[str] = field(default_factory=list)
    advisory: str = ""


class SectorAnalysisEngine:
    """
    Episode 16 Quantitative Sector Engine:
    Manages Sector Weightings, Heavyweight Concentration, Simultaneous Confluence,
    Sector Rotation Cycles, and Portfolio Allocation.
    """

    @staticmethod
    def get_parent_sector(stock_symbol: str) -> SectorName:
        """
        Universal Rule: Returns the primary SectorName for an equity.
        If the sector is ambiguous or unlisted, defaults to Nifty 50 (Universal Umbrella).
        """
        clean_sym = stock_symbol.strip().upper()
        return STOCK_TO_SECTOR_LOOKUP.get(clean_sym, SectorName.NIFTY_50)

    @staticmethod
    def evaluate_heavyweight_concentration(
        sector: SectorName,
        stock_zone_states: Dict[str, str],  # Symbol -> "DEMAND", "SUPPLY", "NEUTRAL"
    ) -> HeavyweightStatusReport:
        """
        Episode 16: The >50% Heavyweight Concentration Rule.
        Evaluates whether the 2-3 stocks driving over 50% of the index are in
        Demand Zones (bullish index propel) or Supply Zones (bearish index drag).
        """
        weights = NSE_SECTOR_WEIGHTINGS.get(sector, {})
        if not weights:
            return HeavyweightStatusReport(
                sector=sector,
                top_heavyweights=[],
                heavyweight_combined_weight_pct=0.0,
                heavyweights_in_demand=[],
                heavyweights_in_supply=[],
                is_heavyweight_momentum_bullish=False,
                explanation=f"No granular weighting data registered for {sector.value}; evaluating via Nifty 50 umbrella.",
            )

        # Sort constituents by weight descending
        sorted_constituents = sorted(weights.items(), key=lambda x: x[1], reverse=True)

        # Select top heavyweights until combined weight crosses 50.0%
        top_hw: List[str] = []
        cum_weight = 0.0
        for sym, wt in sorted_constituents:
            top_hw.append(sym)
            cum_weight += wt
            if cum_weight >= 50.0:
                break

        in_demand: List[str] = []
        in_supply: List[str] = []

        for sym in top_hw:
            state = stock_zone_states.get(sym, "NEUTRAL").upper()
            if state == "DEMAND":
                in_demand.append(sym)
            elif state == "SUPPLY":
                in_supply.append(sym)

        # Heavyweight momentum is bullish if majority of top heavyweights are in Demand
        is_bullish = len(in_demand) >= (len(top_hw) / 2.0) and len(in_demand) > len(in_supply)

        if is_bullish:
            expl = (
                f"Bullish Heavyweight Momentum in {sector.value}: Top heavyweights "
                f"({', '.join(in_demand)}) controlling {cum_weight:.1f}% index weight are in Demand Zones. "
                f"Sector index will propel upward, creating tailwinds for individual constituents."
            )
        elif len(in_supply) > 0:
            expl = (
                f"Bearish Heavyweight Drag in {sector.value}: Heavyweights ({', '.join(in_supply)}) "
                f"are in Supply Zones. Even if low-weight constituents bounce, sector index will face heavy drag."
            )
        else:
            expl = (
                f"Neutral Heavyweight State in {sector.value}: Heavyweights controlling {cum_weight:.1f}% "
                f"are in consolidation without clear zone triggers."
            )

        return HeavyweightStatusReport(
            sector=sector,
            top_heavyweights=top_hw,
            heavyweight_combined_weight_pct=cum_weight,
            heavyweights_in_demand=in_demand,
            heavyweights_in_supply=in_supply,
            is_heavyweight_momentum_bullish=is_bullish,
            explanation=expl,
        )

    @staticmethod
    def evaluate_simultaneous_confluence(
        is_stock_in_demand: bool,
        is_sector_in_demand: bool,
        is_nifty_in_demand: bool,
        is_sector_in_free_fall: bool = False,
    ) -> SectorConfluenceResult:
        """
        Episode 16: The Three Levels of Sector Confluence & Missing Support Filter.
        - Level 1: Only Nifty in Demand Zone -> +0.5 points (Modest macro push).
        - Level 2: Only Stock in Demand Zone -> +0.0 points (Independent bounce).
        - Level 3: Stock + Sector + Nifty ALL in Demand Zones -> +2.0 points (EXPLOSIVE ROCKET MOVE!).
        - Stock + Sector in Demand -> +2.0 points (Supreme Sector Support Add-on).
        - The Missing Support Filter: If stock is in Demand but Sector/Nifty are in free fall,
          flag warning and block long execution.
        """
        # 1. The Missing Support Filter (Episode 16 Rule)
        if is_stock_in_demand and is_sector_in_free_fall:
            return SectorConfluenceResult(
                confluence_level=SectorConfluenceLevel.MISSING_SUPPORT,
                is_stock_in_demand=True,
                is_sector_in_demand=False,
                is_nifty_in_demand=is_nifty_in_demand,
                bonus_points=0.0,
                is_rocket_move=False,
                missing_support_warning=True,
                status_message=(
                    "The Missing Support Trap Detected: Stock is in Demand Zone, but parent sector is in free fall. "
                    "Long execution must be halted; wait for the parent sector to reach historical support."
                ),
            )

        # 2. Level 3: Simultaneous Triad Alignment (Rocket Move)
        if is_stock_in_demand and is_sector_in_demand and is_nifty_in_demand:
            return SectorConfluenceResult(
                confluence_level=SectorConfluenceLevel.LEVEL_3_ROCKET_MOVE,
                is_stock_in_demand=True,
                is_sector_in_demand=True,
                is_nifty_in_demand=True,
                bonus_points=2.0,
                is_rocket_move=True,
                missing_support_warning=False,
                status_message=(
                    "Level 3 Confluence (Explosive Rocket Move!): Stock, Parent Sector, and Nifty 50 are ALL in "
                    "institutional Demand Zones simultaneously. +2 Extra Trade Score awarded. Exceptional statistical edge."
                ),
            )

        # 3. Stock + Sector in Demand (Standard Supreme Add-on)
        if is_stock_in_demand and is_sector_in_demand:
            return SectorConfluenceResult(
                confluence_level=SectorConfluenceLevel.SECTOR_SUPPORTED,
                is_stock_in_demand=True,
                is_sector_in_demand=True,
                is_nifty_in_demand=False,
                bonus_points=2.0,
                is_rocket_move=False,
                missing_support_warning=False,
                status_message=(
                    "Sector Supported (+2 Extra Trade Score): Parent sector is in Demand Zone. "
                    "Macro institutional order flow provides powerful tailwind for individual stock setup."
                ),
            )

        # 4. Level 1: Only Nifty in Demand Zone
        if not is_stock_in_demand and not is_sector_in_demand and is_nifty_in_demand:
            return SectorConfluenceResult(
                confluence_level=SectorConfluenceLevel.LEVEL_1_NIFTY_ONLY,
                is_stock_in_demand=False,
                is_sector_in_demand=False,
                is_nifty_in_demand=True,
                bonus_points=0.5,
                is_rocket_move=False,
                missing_support_warning=False,
                status_message="Level 1 Confluence: Only Nifty 50 is in Demand Zone. Modest broader market push.",
            )

        # 5. Level 2: Only Stock in Demand Zone
        return SectorConfluenceResult(
            confluence_level=SectorConfluenceLevel.LEVEL_2_STOCK_ONLY,
            is_stock_in_demand=is_stock_in_demand,
            is_sector_in_demand=is_sector_in_demand,
            is_nifty_in_demand=is_nifty_in_demand,
            bonus_points=0.0,
            is_rocket_move=False,
            missing_support_warning=False,
            status_message="Level 2 Confluence: Only Stock is in Demand Zone. Stock must bounce independently.",
        )

    @staticmethod
    def evaluate_sector_rotation(
        sector: SectorName,
        current_index_level: float,
        macro_demand_zone: Optional[Tuple[float, float]] = None,
        macro_supply_zone: Optional[Tuple[float, float]] = None,
        tested_overhead_supply_count: int = 0,
        is_at_all_time_high: bool = False,
    ) -> Tuple[SectorRotationPhase, str]:
        """
        Episode 16: Sector Rotation Dynamics.
        - "Sectors Cannot Go to Zero": A national sector index (Metal, PSU Bank, IT) cannot go bankrupt.
          When reaching multi-year lows or historical demand origins, it is a prime institutional accumulation zone.
        - Tested Supply Trendline: Relief rallies testing and exhausting overhead supply clear the runway
          for explosive breakouts once the macro demand base is touched.
        - Peak at ATH: Rotate capital out of 5x run leaders into lagging quality constituents or bottoming sectors.
        """
        if is_at_all_time_high:
            return (
                SectorRotationPhase.PEAK_AT_ALL_TIME_HIGH,
                f"{sector.value} is at All-Time High. Avoid chasing 5x run leaders; "
                f"rotate capital into lagging quality constituents or bottoming sectors (GTF 40-40-20 rule).",
            )

        if macro_demand_zone:
            pl, dl = macro_demand_zone
            if dl <= current_index_level <= pl * 1.05:
                trendline_str = (
                    f" Overhead supply trendline exhausted with {tested_overhead_supply_count} tested supply zones; "
                    f"runway clear for explosive bull run."
                    if tested_overhead_supply_count >= 2
                    else ""
                )
                return (
                    SectorRotationPhase.ACCUMULATION_AT_CYCLE_LOW,
                    f"{sector.value} at Macro Institutional Demand Origin [{dl:.1f} - {pl:.1f}]. "
                    f"Sectors cannot go to zero; prime generational accumulation phase.{trendline_str}",
                )

        if macro_supply_zone:
            pl, dl = macro_supply_zone
            if pl <= current_index_level <= dl:
                return (
                    SectorRotationPhase.DISTRIBUTION_AT_SUPPLY,
                    f"{sector.value} is testing Macro Supply Zone [{pl:.1f} - {dl:.1f}]. "
                    f"Multi-month distribution pressure expected; tighten trailing stops.",
                )

        if tested_overhead_supply_count >= 2:
            return (
                SectorRotationPhase.CORRECTION_WITH_TESTED_SUPPLY,
                f"{sector.value} correcting with {tested_overhead_supply_count} tested overhead supply zones. "
                f"Sellers are depleting inventory on relief bounces.",
            )

        return (
            SectorRotationPhase.EARLY_EXPANSION,
            f"{sector.value} in intermediate expansion phase.",
        )

    @classmethod
    def audit_portfolio_construction(
        cls,
        stock_list: List[str],
        sector_lookup: Optional[Dict[str, SectorName]] = None,
    ) -> PortfolioSectorAllocationReport:
        """
        Episode 16: Long-Term Portfolio Construction Blueprint.
        Rules:
        1. Portfolio Size Limit: Maintain 12 to 15 stocks maximum (dilution beyond 15 creates index-like drag).
        2. Sector Allocation: Hold 2 to 4 stocks across different sectors (prevent industry over-concentration).
        3. Rotation Arbitrage: Identifies lagging quality constituents in high-momentum sectors.
        """
        total_stocks = len(stock_list)
        rejection_reasons: List[str] = []

        if total_stocks < 12:
            rejection_reasons.append(
                f"Under-diversified Portfolio: Contains {total_stocks} stocks (Minimum 12 required to prevent single-stock operational catastrophe)."
            )
        elif total_stocks > 15:
            rejection_reasons.append(
                f"Over-diversified Portfolio: Contains {total_stocks} stocks (Maximum 15 allowable; over-diversification dilutes returns into index performance)."
            )

        # Count stocks per sector
        stocks_per_sec: Dict[str, int] = {}
        sectors_set = set()

        for sym in stock_list:
            clean_sym = sym.strip().upper()
            sec = sector_lookup.get(clean_sym) if sector_lookup else cls.get_parent_sector(clean_sym)
            sec_name = sec.value
            sectors_set.add(sec)
            stocks_per_sec[sec_name] = stocks_per_sec.get(sec_name, 0) + 1

        # Check for over-concentration (>4 stocks in one sector)
        for sec_name, count in stocks_per_sec.items():
            if count > 4:
                rejection_reasons.append(
                    f"Sector Over-concentration: {sec_name} holds {count} stocks (Maximum allowable is 2 to 4 stocks per sector)."
                )

        is_valid = len(rejection_reasons) == 0

        if is_valid:
            advisory = (
                f"Optimal Portfolio Allocation: {total_stocks} stocks diversified across "
                f"{len(sectors_set)} sectors with 2-4 stocks per industry (GTF 40-40-20 Compliant)."
            )
        else:
            advisory = f"Portfolio Allocation Non-Compliant: {'; '.join(rejection_reasons)}"

        return PortfolioSectorAllocationReport(
            is_allocation_valid=is_valid,
            total_stocks_count=total_stocks,
            sectors_represented=list(sectors_set),
            stocks_per_sector=stocks_per_sec,
            rejection_reasons=rejection_reasons,
            advisory=advisory,
        )
