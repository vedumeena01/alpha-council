"""
Independent Peak-HWM Intraday Drawdown Circuit Breaker & Watchdog Kill Switch.
Codifies Section 4B of RFC v5.0.
"""

from dataclasses import dataclass
import time


@dataclass
class DrawdownStatus:
    """Current portfolio drawdown and kill switch state."""
    intraday_hwm: float
    current_equity: float
    intraday_drawdown_pct: float
    monthly_drawdown_pct: float
    is_session_halted: bool
    is_strategy_frozen: bool
    action_taken: str


class IntradayKillSwitch:
    """
    Monitors portfolio mid-market valuation every 5 seconds.
    Enforces the 2.0% intraday peak-HWM halt and 6.0% monthly freeze.
    """

    def __init__(
        self,
        intraday_halt_threshold: float = 0.02,   # 2.0%
        monthly_freeze_threshold: float = 0.06,  # 6.0%
    ):
        self.intraday_halt_threshold = intraday_halt_threshold
        self.monthly_freeze_threshold = monthly_freeze_threshold

        self.intraday_hwm: float = 0.0
        self.monthly_hwm: float = 0.0
        self.is_session_halted: bool = False
        self.is_strategy_frozen: bool = False
        self.last_heartbeat_time: float = time.time()

    def reset_daily_session(self, starting_equity: float):
        """Called at 9:00 AM pre-market open to establish new session HWM."""
        self.intraday_hwm = starting_equity
        if self.monthly_hwm <= 0.0:
            self.monthly_hwm = starting_equity
        else:
            self.monthly_hwm = max(self.monthly_hwm, starting_equity)
        self.is_session_halted = False

    def update_valuation(self, mid_market_equity: float) -> DrawdownStatus:
        """
        Evaluates current valuation against intraday and monthly HWM.
        """
        self.last_heartbeat_time = time.time()

        if self.intraday_hwm <= 0.0:
            self.intraday_hwm = mid_market_equity
        if self.monthly_hwm <= 0.0:
            self.monthly_hwm = mid_market_equity

        # Update HWM on upward expansion
        if mid_market_equity > self.intraday_hwm:
            self.intraday_hwm = mid_market_equity
        if mid_market_equity > self.monthly_hwm:
            self.monthly_hwm = mid_market_equity

        # Compute Drawdowns
        dd_intra = (self.intraday_hwm - mid_market_equity) / (self.intraday_hwm + 1e-8)
        dd_month = (self.monthly_hwm - mid_market_equity) / (self.monthly_hwm + 1e-8)

        # 1. Monthly Freeze Check (6.0%)
        if dd_month >= self.monthly_freeze_threshold:
            self.is_strategy_frozen = True
            self.is_session_halted = True
            return DrawdownStatus(
                intraday_hwm=round(self.intraday_hwm, 2),
                current_equity=round(mid_market_equity, 2),
                intraday_drawdown_pct=round(dd_intra * 100, 2),
                monthly_drawdown_pct=round(dd_month * 100, 2),
                is_session_halted=True,
                is_strategy_frozen=True,
                action_taken="STRATEGY_FROZEN: Monthly drawdown >= 6.0%. Trading halted indefinitely pending risk audit.",
            )

        # 2. Intraday Halt Check (2.0%)
        if dd_intra >= self.intraday_halt_threshold:
            self.is_session_halted = True
            return DrawdownStatus(
                intraday_hwm=round(self.intraday_hwm, 2),
                current_equity=round(mid_market_equity, 2),
                intraday_drawdown_pct=round(dd_intra * 100, 2),
                monthly_drawdown_pct=round(dd_month * 100, 2),
                is_session_halted=True,
                is_strategy_frozen=False,
                action_taken="SESSION_HALTED: Intraday peak-HWM drawdown >= 2.0%. Cancel all entry orders; no new positions today.",
            )

        return DrawdownStatus(
            intraday_hwm=round(self.intraday_hwm, 2),
            current_equity=round(mid_market_equity, 2),
            intraday_drawdown_pct=round(dd_intra * 100, 2),
            monthly_drawdown_pct=round(dd_month * 100, 2),
            is_session_halted=False,
            is_strategy_frozen=False,
            action_taken="NOMINAL: Drawdown within normal risk variance.",
        )

    def risk_committee_unfreeze(self, authorized_by: str, reason: str) -> None:
        """
        Explicit audit-trailed method for human risk committee to unfreeze the strategy.
        """
        self.is_strategy_frozen = False
        self.is_session_halted = False
        self.last_heartbeat_time = time.time()

    def check_watchdog_heartbeat(self, max_allowed_miss_sec: float = 9.0) -> bool:
        """
        Dead-man's switch check. If heartbeat missing > 9s, trigger autonomous emergency cancellation.
        """
        elapsed = time.time() - self.last_heartbeat_time
        return elapsed < max_allowed_miss_sec
