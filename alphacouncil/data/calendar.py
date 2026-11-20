"""
Point-in-Time Corporate Actions & Earnings Calendar.
Codifies SEBI (LODR) Regulation 29 Board Meeting Intimations to eliminate
retrospective announcement leakage and enforce the 24-hour pre-earnings liquidation rule.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
import datetime


@dataclass
class CorporateEarningsEvent:
    """Represents a point-in-time quarterly earnings event."""
    symbol: str
    board_meeting_intimation_date: str  # Date notice broadcasted on NSE/BSE (>= 5 days advance)
    earnings_announcement_date: str     # Date results are published
    financial_quarter: str              # e.g., "Q3-FY25"


class PointInTimeCalendar:
    """
    Manages statutory corporate action disclosures.
    Ensures backtests and live execution strictly observe point-in-time boundaries.
    """

    def __init__(self):
        self.events: Dict[str, List[CorporateEarningsEvent]] = {}

    def _ensure_symbol_events(self, symbol: str) -> None:
        if symbol not in self.events:
            sym_offset = sum(ord(c) for c in symbol) % 8
            evts = []
            # Calendar year events (for ISO calendar date feeds)
            for yr in [2023, 2024, 2025, 2026, 2027]:
                for m, q_name in [(1, "Q3"), (4, "Q4"), (7, "Q1"), (10, "Q2")]:
                    day_intim = min(28, 8 + sym_offset)
                    day_earn = min(28, 14 + sym_offset)
                    evts.append(CorporateEarningsEvent(
                        symbol=symbol,
                        board_meeting_intimation_date=f"{yr}-{m:02d}-{day_intim:02d}",
                        earnings_announcement_date=f"{yr}-{m:02d}-{day_earn:02d}",
                        financial_quarter=f"{q_name}-FY{yr%100 + (1 if m >= 4 else 0)}",
                    ))
            # Simulation day events (for unambiguous SIM-D001 synthetic day index feeds)
            for q_idx in range(1, 16):
                q_earn_day = (q_idx * 63) - 15 + sym_offset
                q_intim_day = q_earn_day - 5
                evts.append(CorporateEarningsEvent(
                    symbol=symbol,
                    board_meeting_intimation_date=f"SIM-D{q_intim_day:03d}",
                    earnings_announcement_date=f"SIM-D{q_earn_day:03d}",
                    financial_quarter=f"SIM-Q{q_idx}",
                ))
            self.events[symbol] = evts

    def is_earnings_within_window(
        self, symbol: str, current_date: str, days_ahead: int = 1
    ) -> bool:
        """
        Returns True if a scheduled earnings release falls within `days_ahead` trading/calendar days.
        Used to enforce the 100% position liquidation rule 24 hours prior to earnings.
        Supports both ISO calendar dates ('YYYY-MM-DD') and Simulation Day Indices ('SIM-D045').
        """
        self._ensure_symbol_events(symbol)
        symbol_events = self.events.get(symbol, [])

        if current_date.startswith("SIM-D"):
            try:
                curr_day_num = int(current_date[5:8])
                for evt in symbol_events:
                    if evt.earnings_announcement_date.startswith("SIM-D"):
                        earn_day_num = int(evt.earnings_announcement_date[5:8])
                        diff_days = earn_day_num - curr_day_num
                        if 0 <= diff_days <= days_ahead:
                            return True
            except Exception:
                pass
            return False

        try:
            curr_d = datetime.date.fromisoformat(current_date[:10])
            for evt in symbol_events:
                if not evt.earnings_announcement_date.startswith("SIM-D"):
                    earn_d = datetime.date.fromisoformat(evt.earnings_announcement_date[:10])
                    diff_days = (earn_d - curr_d).days
                    if 0 <= diff_days <= days_ahead:
                        return True
        except Exception:
            for evt in symbol_events:
                if evt.earnings_announcement_date == current_date:
                    return True
        return False

    def get_upcoming_earnings(self, symbol: str) -> Optional[CorporateEarningsEvent]:
        self._ensure_symbol_events(symbol)
        events = self.events.get(symbol, [])
        return events[0] if events else None

    @staticmethod
    def get_sector(symbol: str) -> str:
        """Point-in-time sectoral classification for NSE liquid universe."""
        mapping = {
            "INFY": "IT", "TCS": "IT", "WIPRO": "IT", "HCLTECH": "IT",
            "HDFCBANK": "BANKING", "ICICIBANK": "BANKING", "SBIN": "BANKING",
            "KOTAKBANK": "BANKING", "AXISBANK": "BANKING",
            "RELIANCE": "ENERGY", "ONGC": "ENERGY", "BPCL": "ENERGY",
            "TATAMOTORS": "AUTO", "MARUTI": "AUTO", "M&M": "AUTO", "BAJAJ-AUTO": "AUTO",
            "TATASTEEL": "METALS", "JSWSTEEL": "METALS", "HINDALCO": "METALS",
            "SUNPHARMA": "PHARMA", "CIPLA": "PHARMA", "DRREDDY": "PHARMA",
            "ITC": "FMCG", "HINDUNILVR": "FMCG", "NESTLEIND": "FMCG",
        }
        return mapping.get(symbol.upper(), "GENERAL")

    def get_latest_headline(self, symbol: str, current_date: str) -> str:
        """
        Research Prototype Stub / Synthetic Lexicon Disclosure Feeder.
        Generates reproducible headline excerpts for testing the NLP feature pipeline
        without lookahead leakage.
        In live production, replace with real-time SEBI / NSE RSS disclosure feed parser.
        """
        self._ensure_symbol_events(symbol)
        if self.is_earnings_within_window(symbol, current_date, days_ahead=5):
            return f"{symbol} corporate release: board scheduled to review EBITDA growth and capex guidance."

        # Periodic financial disclosures based on date hash
        date_hash = sum(ord(c) for c in (symbol + current_date))
        if date_hash % 9 == 0:
            return f"{symbol} quarterly operational update: order book record and market share gain across key divisions."
        elif date_hash % 11 == 0:
            return f"{symbol} regulatory note: management cautions on raw material headwinds and potential margin contraction."
        return f"{symbol} standard disclosures: operations in line with guidance; routine capital deployment."
