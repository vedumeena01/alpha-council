"""
GTF Institutional Risk Management & Capital Protection Engine (Episode 10).
Codifies the Exact Position Sizing Formula, Monetary Risk Invariance,
The 10 Trades/Month Cap, Anti-Tampering SL Guards, The 100-Trade Journal,
and Quantitative Excel Growth Models.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple
import math


class RiskTier(float, Enum):
    """
    Episode 10: Risk Per Trade (RPT) Hierarchy.
    Determines maximum monetary risk percentage of total capital allocated per trade.
    """
    LEARNING = 0.005       # 0.5% (Early practice, absorbs early mistakes cheaply)
    BEGINNER = 0.010       # 1.0% (First 1-3 months of live trading)
    INTERMEDIATE = 0.015   # 1.5% (Proven consistency)
    PRO = 0.020            # 2.0% (Absolute ceiling - never exceed)


class ExecutionErrorType(str, Enum):
    """
    Episode 10 Concept 11: The 40-Mistake Rule Categories.
    'A mistake repeated more than once is a decision.'
    """
    TREND_CONFLICT = "TREND_CONFLICT"
    OVERHEAD_HTF_SUPPLY_TRAP = "OVERHEAD_HTF_SUPPLY_TRAP"
    UNPROVEN_CANDLE_CLOSE = "UNPROVEN_CANDLE_CLOSE"
    FO_LOT_SIZE_OVERLEVERAGE = "FO_LOT_SIZE_OVERLEVERAGE"
    NEWS_HEADLINE_TRAP = "NEWS_HEADLINE_TRAP"
    CHASING_MISSED_ENTRY = "CHASING_MISSED_ENTRY"
    STOPLOSS_WIDENED_POST_ENTRY = "STOPLOSS_WIDENED_POST_ENTRY"
    AVERAGING_DOWN = "AVERAGING_DOWN"
    MONTHLY_TRADE_CAP_BREACH = "MONTHLY_TRADE_CAP_BREACH"
    ARBITRARY_QUANTITY = "ARBITRARY_QUANTITY"


@dataclass
class SizingBreakdown:
    """Exact mathematical position sizing breakdown."""
    capital: float
    risk_tier: RiskTier
    risk_per_trade_inr: float
    entry_price: float
    stop_loss_price: float
    risk_distance_points: float
    quantity_shares: int
    actual_monetary_risk_inr: float
    total_capital_required_inr: float
    is_sizing_valid: bool
    rationale: str


@dataclass
class GrowthProjection:
    """Quantitative growth projection (The Excel Growth Model)."""
    capital: float
    risk_tier: RiskTier
    win_rate: float
    target_rrr: float
    num_trades: int
    wins_count: int
    losses_count: int
    risk_per_trade: float
    gain_per_win: float
    total_gain: float
    total_loss: float
    net_monthly_profit: float
    monthly_return_pct: float
    annual_return_pct: float


@dataclass
class TradeLogEntry:
    """Record entry for the GTF 100-Trade Journal."""
    trade_id: int
    date: str
    symbol: str
    entry_price: float
    stop_loss: float
    target_price: float
    quantity: int
    outcome: str  # "TARGET_HIT", "STOP_LOSS_HIT", "OPEN"
    pnl_inr: float = 0.0
    mistakes: List[ExecutionErrorType] = field(default_factory=list)
    notes: str = ""


class GTFTradingJournal:
    """
    Episode 10 Concept 6 & 11: The Mandatory 100-Trade Journal.
    Enforces:
    1. Maximum 10 trades per calendar month.
    2. The 100-trade commitment before judging a strategy.
    3. The 40-mistake elimination tracker ('never repeat the same mistake twice').
    """

    MAX_TRADES_PER_MONTH: int = 10
    TARGET_COMMITMENT_TRADES: int = 100

    def __init__(self, initial_capital: float = 100000.0):
        self.initial_capital = initial_capital
        self.trades: List[TradeLogEntry] = []
        self.mistake_counts: Dict[ExecutionErrorType, int] = {e: 0 for e in ExecutionErrorType}

    def log_trade(self, entry: TradeLogEntry) -> Tuple[bool, str]:
        """
        Logs a trade into the journal.
        Enforces monthly cap and tracks repetitive mistakes.
        """
        # Count trades in the same month (extract YYYY-MM)
        month_str = entry.date[:7] if len(entry.date) >= 7 else "CURRENT"
        current_month_count = sum(1 for t in self.trades if t.date[:7] == month_str)

        if current_month_count >= self.MAX_TRADES_PER_MONTH:
            return (
                False,
                f"Monthly Cap Reached: Already executed {current_month_count}/{self.MAX_TRADES_PER_MONTH} trades for {month_str}. "
                "Ruthlessly filter; do not overtrade.",
            )

        # Track mistakes
        repeat_warnings = []
        for m in entry.mistakes:
            self.mistake_counts[m] += 1
            if self.mistake_counts[m] > 1:
                repeat_warnings.append(f"Repeat Mistake Detected: {m.value} logged {self.mistake_counts[m]} times!")

        self.trades.append(entry)
        msg = f"Trade #{len(self.trades)} logged successfully."
        if repeat_warnings:
            msg += " " + " ".join(repeat_warnings)
        return True, msg

    @property
    def total_trades_count(self) -> int:
        return len(self.trades)

    @property
    def is_100_trade_commitment_fulfilled(self) -> bool:
        return len(self.trades) >= self.TARGET_COMMITMENT_TRADES


class GTFRiskManager:
    """
    Core Risk Management Engine taught by Arun Singh Tanwar.
    """

    @staticmethod
    def calculate_position_size(
        capital: float,
        risk_tier: RiskTier,
        entry_price: float,
        stop_loss: float,
    ) -> SizingBreakdown:
        """
        Episode 10 Concept 3: The Exact Position Sizing Formula.
        Quantity = floor(Risk_Per_Trade / abs(Entry - StopLoss))
        Ensures monetary loss on an SL hit is strictly identical regardless of share price.
        """
        risk_distance = abs(entry_price - stop_loss)
        if risk_distance <= 0.0:
            return SizingBreakdown(
                capital=capital,
                risk_tier=risk_tier,
                risk_per_trade_inr=0.0,
                entry_price=entry_price,
                stop_loss_price=stop_loss,
                risk_distance_points=0.0,
                quantity_shares=0,
                actual_monetary_risk_inr=0.0,
                total_capital_required_inr=0.0,
                is_sizing_valid=False,
                rationale="Invalid stop-loss distance (cannot be zero).",
            )

        rpt_inr = round(capital * risk_tier.value, 2)
        qty = int(math.floor(rpt_inr / risk_distance))
        actual_risk = round(qty * risk_distance, 2)
        capital_req = round(qty * entry_price, 2)

        is_valid = qty > 0

        rationale = (
            f"Capital: ₹{capital:,.2f} | Tier: {risk_tier.name} ({risk_tier.value*100:.1f}%) | "
            f"RPT: ₹{rpt_inr:,.2f} | Risk Points: ₹{risk_distance:.2f} | "
            f"Quantity: {qty} shares | Actual Max Loss: ₹{actual_risk:,.2f} | "
            f"Capital Required: ₹{capital_req:,.2f}."
        )

        return SizingBreakdown(
            capital=capital,
            risk_tier=risk_tier,
            risk_per_trade_inr=rpt_inr,
            entry_price=entry_price,
            stop_loss_price=stop_loss,
            risk_distance_points=risk_distance,
            quantity_shares=qty,
            actual_monetary_risk_inr=actual_risk,
            total_capital_required_inr=capital_req,
            is_sizing_valid=is_valid,
            rationale=rationale,
        )

    @staticmethod
    def detect_anti_tamper_violations(
        original_entry: float,
        current_market_price: float,
        original_sl: float,
        new_sl: float,
        is_demand: bool = True,
        is_averaging_down: bool = False,
        chase_threshold_pct: float = 0.015,
    ) -> Tuple[bool, List[str]]:
        """
        Episode 10 Concept 4: Anti-Tamper & Critical Execution Error Guards.
        1. Chasing Missed Entry: CMP already rallied significantly past entry.
        2. Modifying/Widening Stop-Loss: Expanding SL distance post-entry.
        3. Averaging Down: Adding to losing position.
        """
        violations: List[str] = []

        # 1. Chasing Missed Entry
        if is_demand:
            if current_market_price > original_entry * (1.0 + chase_threshold_pct):
                violations.append(
                    f"Chasing Missed Entry Prohibited: CMP ₹{current_market_price:.2f} is "
                    f"> {chase_threshold_pct*100:.1f}% above entry ₹{original_entry:.2f}. "
                    "Let the trade go; missing costs ₹0."
                )
        else:
            if current_market_price < original_entry * (1.0 - chase_threshold_pct):
                violations.append(
                    f"Chasing Missed Short Prohibited: CMP ₹{current_market_price:.2f} is "
                    f"> {chase_threshold_pct*100:.1f}% below entry ₹{original_entry:.2f}."
                )

        # 2. Widening Stop-Loss
        if is_demand:
            if new_sl < original_sl:
                violations.append(
                    f"Stop-Loss Widening Prohibited: Moving SL down from ₹{original_sl:.2f} to ₹{new_sl:.2f} "
                    "inflates risk exponentially. Maintain original stop."
                )
        else:
            if new_sl > original_sl:
                violations.append(
                    f"Stop-Loss Widening Prohibited: Moving short SL up from ₹{original_sl:.2f} to ₹{new_sl:.2f}."
                )

        # 3. Averaging Down
        if is_averaging_down:
            violations.append(
                "Averaging Down Trap: Adding shares to a position falling through a demand zone is strictly prohibited."
            )

        is_clean = len(violations) == 0
        return is_clean, violations

    @staticmethod
    def project_growth(
        capital: float = 100000.0,
        risk_tier: RiskTier = RiskTier.BEGINNER,
        win_rate: float = 0.50,
        target_rrr: float = 2.0,
        num_trades: int = 10,
    ) -> GrowthProjection:
        """
        Episode 10 Concept 7: Quantitative Excel Growth Model.
        Calculates expected returns based on 10 trades per month and Risk-to-Reward ratio.
        """
        wins = int(round(num_trades * win_rate))
        losses = num_trades - wins
        rpt = capital * risk_tier.value
        gain_per_win = rpt * target_rrr

        total_gain = wins * gain_per_win
        total_loss = losses * rpt
        net_profit = total_gain - total_loss
        monthly_return_pct = round((net_profit / capital) * 100.0, 2)
        annual_return_pct = round(monthly_return_pct * 12.0, 2)

        return GrowthProjection(
            capital=capital,
            risk_tier=risk_tier,
            win_rate=win_rate,
            target_rrr=target_rrr,
            num_trades=num_trades,
            wins_count=wins,
            losses_count=losses,
            risk_per_trade=rpt,
            gain_per_win=gain_per_win,
            total_gain=total_gain,
            total_loss=total_loss,
            net_monthly_profit=net_profit,
            monthly_return_pct=monthly_return_pct,
            annual_return_pct=annual_return_pct,
        )
