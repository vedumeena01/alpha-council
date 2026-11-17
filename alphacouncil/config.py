"""
Institutional Configuration for AlphaCouncil.
All parameters strictly codified per RFC v5.0 specification and regulatory schedules.
"""

from typing import List
from pydantic import BaseModel, Field


class StatutoryFeeConfig(BaseModel):
    """NSE/SEBI statutory transaction fee schedule (Effective Oct 1, 2024)."""
    stt_delivery_rate: float = Field(default=0.0010, description="0.10% on buy and sell delivery")
    stt_intraday_sell_rate: float = Field(default=0.00025, description="0.025% on intraday sell")
    brokerage_per_order_cap: float = Field(default=20.0, description="₹20 flat per order cap")
    brokerage_rate: float = Field(default=0.0005, description="0.05% or ₹20 whichever is lower")
    exchange_txn_charge_rate: float = Field(default=0.0000297, description="0.00297% revised NSE charge")
    sebi_turnover_rate: float = Field(default=0.000001, description="₹10 per Crore (0.0001%)")
    stamp_duty_buy_rate: float = Field(default=0.00015, description="0.015% on buy side only")
    gst_rate: float = Field(default=0.18, description="18% GST on (Brokerage + Txn + SEBI)")
    market_impact_gamma: float = Field(default=0.314, description="Almgren-Chriss square-root impact constant")
    max_adv_participation: float = Field(default=0.025, description="2.5% maximum interval ADV participation")


class RiskParameters(BaseModel):
    """Institutional Risk Limits and Guardrail Configuration."""
    base_risk_fraction: float = Field(default=0.010, description="1.0% base equity risk per trade")
    max_risk_ceiling: float = Field(default=0.015, description="1.5% maximum allowable risk per trade")
    target_annual_volatility: float = Field(default=0.15, description="15% annualized portfolio volatility target")
    max_single_stock_notional_pct: float = Field(default=0.20, description="20% max single-stock equity concentration")
    intraday_hwm_drawdown_limit: float = Field(default=0.02, description="2.0% peak-HWM intraday session halt")
    monthly_drawdown_freeze_limit: float = Field(default=0.06, description="6.0% monthly drawdown committee freeze")
    circuit_proximity_threshold: float = Field(default=0.015, description="1.5% distance threshold from circuit bands")
    mwpl_ban_entry_threshold: float = Field(default=0.95, description="95% MWPL F&O derivative hedge ban entry")
    mwpl_ban_exit_threshold: float = Field(default=0.80, description="80% MWPL F&O derivative hedge ban exit")
    min_atr_stop_multiple: float = Field(default=1.0, description="Skip setup if stop distance < 1.0 * ATR14")
    cold_start_trade_threshold: int = Field(default=200, description="Bypass Kelly until 200 trades closed")
    rolling_calibration_window: int = Field(default=250, description="Rolling window for Brier Skill Score")


class AlphaCouncilConfig(BaseModel):
    """Global system configuration container."""
    system_name: str = "AlphaCouncil"
    version: str = "1.0.0"
    base_currency: str = "INR"
    initial_equity: float = Field(default=10_000_000.0, description="₹1 Crore default equity")
    target_universe: List[str] = Field(
        default_factory=lambda: [
            "RELIANCE", "INFY", "TCS", "HDFCBANK", "ICICIBANK",
            "BHARTIARTL", "LT", "SBIN", "HINDUNILVR", "ITC"
        ]
    )
    fees: StatutoryFeeConfig = Field(default_factory=StatutoryFeeConfig)
    risk: RiskParameters = Field(default_factory=RiskParameters)


# Global default configuration instance
DEFAULT_CONFIG = AlphaCouncilConfig()
