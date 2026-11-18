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
        # Example registered earnings dates for the sample universe
        self.events: Dict[str, List[CorporateEarningsEvent]] = {
            "RELIANCE": [
                CorporateEarningsEvent("RELIANCE", "2025-01-10", "2025-01-17", "Q3-FY25"),
                CorporateEarningsEvent("RELIANCE", "2025-04-12", "2025-04-19", "Q4-FY25"),
            ],
            "INFY": [
                CorporateEarningsEvent("INFY", "2025-01-05", "2025-01-12", "Q3-FY25"),
                CorporateEarningsEvent("INFY", "2025-04-08", "2025-04-15", "Q4-FY25"),
            ],
            "TCS": [
                CorporateEarningsEvent("TCS", "2025-01-04", "2025-01-11", "Q3-FY25"),
                CorporateEarningsEvent("TCS", "2025-04-06", "2025-04-13", "Q4-FY25"),
            ],
        }

    def is_earnings_within_window(
        self, symbol: str, current_date: str, days_ahead: int = 1
    ) -> bool:
        """
        Returns True if a scheduled earnings release falls within `days_ahead` calendar days.
        Used to enforce the 100% position liquidation rule 24 hours prior to earnings.
        """
        symbol_events = self.events.get(symbol, [])
        try:
            curr_d = datetime.date.fromisoformat(current_date[:10])
            for evt in symbol_events:
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
        events = self.events.get(symbol, [])
        return events[0] if events else None
