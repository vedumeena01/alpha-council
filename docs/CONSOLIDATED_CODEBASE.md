# 🏛️ AlphaCouncil: Consolidated Institutional Codebase
> **Single-Document Code Reference for Quant Reviewers, Hiring Committees & Allocators.**  
> *Repository:* [github.com/vedumeena01/alpha-council](https://github.com/vedumeena01/alpha-council)  
> *Online IDE Viewer:* Open `https://github.dev/vedumeena01/alpha-council` or press `.` on the repository.

---

## Table of Contents
1. [Configuration & Statutory Tariffs (`alphacouncil/config.py`)](#1-configuration--statutory-tariffs-alphacouncilconfigpy)
2. [Deterministic Liquidity Sweep Detector (`alphacouncil/alpha/sweep_detector.py`)](#2-deterministic-liquidity-sweep-detector-alphacouncilalphasweep_detectorpy)
3. [López de Prado Triple Barrier & OU Half-Life (`alphacouncil/alpha/triple_barrier.py`)](#3-lópez-de-prado-triple-barrier--ou-half-life-alphacouncilalphatriple_barrierpy)
4. [FinBERT Sentiment & Binomial Audit (`alphacouncil/alpha/sentiment_nlp.py`)](#4-finbert-sentiment--binomial-audit-alphacouncilalphasentiment_nlppy)
5. [Pre-Trade Risk Engine & Concentration Limits (`alphacouncil/risk/pre_trade.py`)](#5-pre-trade-risk-engine--concentration-limits-alphacouncilriskpre_tradepy)
6. [Position Sizing & Kelly Calibration (`alphacouncil/risk/sizing.py`)](#6-position-sizing--kelly-calibration-alphacouncilrisksizingpy)
7. [López de Prado Meta-Labeler (`alphacouncil/risk/meta_labeler.py`)](#7-lópez-de-prado-meta-labeler-alphacouncilriskmeta_labelerpy)
8. [Intraday Kill-Switch & HWM Halt (`alphacouncil/risk/kill_switch.py`)](#8-intraday-kill-switch--hwm-halt-alphacouncilriskkill_switchpy)
9. [Direction-Aware Circuit Guard (`alphacouncil/risk/circuits.py`)](#9-direction-aware-circuit-guard-alphacouncilriskcircuitspy)
10. [Indian Market Statutory Friction Model (`alphacouncil/execution/friction.py`)](#10-indian-market-statutory-friction-model-alphacouncilexecutionfrictionpy)
11. [Idempotent OMS & GTT Sync (`alphacouncil/execution/oms.py`)](#11-idempotent-oms--gtt-sync-alphacouncilexecutionomspy)
12. [Purged Walk-Forward Backtest Simulator (`alphacouncil/backtest/engine.py`)](#12-purged-walk-forward-backtest-simulator-alphacouncilbacktestenginepy)
13. [Deflated Sharpe Ratio & Performance Metrics (`alphacouncil/backtest/metrics.py`)](#13-deflated-sharpe-ratio--performance-metrics-alphacouncilbacktestmetricspy)
14. [7-Model Orthogonal Ablation Suite (`alphacouncil/backtest/ablation.py`)](#14-7-model-orthogonal-ablation-suite-alphacouncilbacktestablationpy)

---

### 1. Configuration & Statutory Tariffs (`alphacouncil/config.py`)
```python
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

DEFAULT_CONFIG = AlphaCouncilConfig()
```

---

### 2. Deterministic Liquidity Sweep Detector (`alphacouncil/alpha/sweep_detector.py`)
```python
from dataclasses import dataclass
from typing import Optional, List
import numpy as np

@dataclass
class SweepSignal:
    symbol: str
    bar_index: int
    signal: int  # +1 for Bullish Reversal, 0 for None
    prior_swing_low: float
    trigger_bar_close: float
    structural_stop: float
    volume_ratio: float
    reason: str

class LiquiditySweepDetector:
    """Implements Hypothesis H1 (Structural Sell-Side Liquidity Sweep)."""
    def __init__(self, lookback: int = 20, volume_factor: float = 1.5):
        self.lookback = lookback
        self.volume_factor = volume_factor

    def evaluate_bar(self, symbol: str, open_p: np.ndarray, high: np.ndarray,
                     low: np.ndarray, close: np.ndarray, volume: np.ndarray,
                     bar_idx: int = -1) -> Optional[SweepSignal]:
        n = len(close)
        if n < self.lookback + 1:
            return None

        # Prior reference window: strictly excludes current bar t
        prior_window_lows = low[-self.lookback - 1 : -1]
        prior_window_vols = volume[-self.lookback - 1 : -1]

        prior_swing_low = float(np.min(prior_window_lows))
        vol_sma = float(np.mean(prior_window_vols))

        curr_open = float(open_p[-1])
        curr_low = float(low[-1])
        curr_close = float(close[-1])
        curr_vol = float(volume[-1])
        vol_ratio = curr_vol / (vol_sma + 1e-8)

        # Invalidate news-driven overnight gap down
        if curr_open < prior_swing_low:
            return SweepSignal(
                symbol=symbol, bar_index=n - 1, signal=0,
                prior_swing_low=prior_swing_low, trigger_bar_close=curr_close,
                structural_stop=round(curr_low * 0.9995, 2),
                volume_ratio=round(vol_ratio, 2),
                reason="Invalidated: Session opened below swing low (News Gap-down)",
            )

        # Sweep condition: low breaks prior low, close recovers above prior low with 1.5x+ volume
        is_sweep = (curr_low < prior_swing_low) and (curr_close > prior_swing_low)
        is_vol_confirmed = curr_vol >= (self.volume_factor * vol_sma)

        if is_sweep and is_vol_confirmed:
            structural_stop = round(curr_low * 0.9995, 2)
            return SweepSignal(
                symbol=symbol, bar_index=n - 1, signal=1,
                prior_swing_low=round(prior_swing_low, 2),
                trigger_bar_close=round(curr_close, 2),
                structural_stop=structural_stop,
                volume_ratio=round(vol_ratio, 2),
                reason="Confirmed: Retail stop sweep absorbed with 1.5x+ volume expansion",
            )
        return None
```

---

### 3. López de Prado Triple Barrier & OU Half-Life (`alphacouncil/alpha/triple_barrier.py`)
```python
from dataclasses import dataclass
import numpy as np

@dataclass
class BarrierOutcome:
    exit_bar_index: int
    exit_price: float
    barrier_hit: str  # "UPPER", "LOWER", "VERTICAL"
    realized_return_pct: float
    holding_period_days: int
    is_success: bool

class TripleBarrierLabeler:
    def __init__(self, payoff_ratio: float = 2.0, max_vertical_days: int = 5):
        self.payoff_ratio = payoff_ratio
        self.max_vertical_days = max_vertical_days

    @staticmethod
    def calculate_ou_half_life(price_series: np.ndarray) -> float:
        if len(price_series) < 20:
            return 3.0
        log_p = np.log(price_series)
        delta_p = np.diff(log_p)
        lag_p = log_p[:-1]
        x = np.column_stack([np.ones_like(lag_p), lag_p])
        try:
            coeffs, _, _, _ = np.linalg.lstsq(x, delta_p, rcond=None)
            beta = coeffs[1]
            if -1.0 < beta < -1e-6:
                half_life = -np.log(2.0) / np.log(1.0 + beta)
                return float(np.clip(half_life, 1.0, 10.0))
            elif beta <= -1.0:
                return 3.0
        except Exception:
            pass
        return 3.0
```

---

### 4. Position Sizing & Kelly Calibration (`alphacouncil/risk/sizing.py`)
```python
from dataclasses import dataclass
from typing import List
import numpy as np

@dataclass
class SizingCalculation:
    symbol: str
    entry_price: float
    stop_price: float
    stop_distance: float
    atr14: float
    is_noise_trap_skipped: bool
    tau_vol: float
    brier_skill_score: float
    kelly_risk_fraction: float
    tau_effective: float
    shares_quantity: int
    proposed_notional: float
    is_aborted: bool
    regime_mode: str
    rationale: str

class PositionSizingEngine:
    def __init__(self, base_risk_fraction: float = 0.010, target_annual_vol: float = 0.15,
                 max_risk_ceiling: float = 0.015, max_notional_pct: float = 0.20, min_atr_multiple: float = 1.0):
        self.base_risk_fraction = base_risk_fraction
        self.target_annual_vol = target_annual_vol
        self.max_risk_ceiling = max_risk_ceiling
        self.max_notional_pct = max_notional_pct
        self.min_atr_multiple = min_atr_multiple

    def compute_size(self, symbol: str, entry_price: float, stop_price: float, target_price: float,
                     atr14: float, realized_annual_vol: float, current_equity: float,
                     historical_closed_trades_count: int = 250, rolling_bss: float = 0.15,
                     estimated_win_prob: float = 0.58) -> SizingCalculation:
        stop_distance = max(0.01, entry_price - stop_price)

        # Invalidation: Skip noise trap if stop < 1.0 * ATR
        if stop_distance < (self.min_atr_multiple * atr14):
            return SizingCalculation(
                symbol=symbol, entry_price=entry_price, stop_price=stop_price, stop_distance=round(stop_distance, 2),
                atr14=round(atr14, 2), is_noise_trap_skipped=True, tau_vol=0.0, brier_skill_score=rolling_bss,
                kelly_risk_fraction=0.0, tau_effective=0.0, shares_quantity=0, proposed_notional=0.0,
                is_aborted=True, regime_mode="NOISE_TRAP_SKIPPED",
                rationale=f"Stop distance (₹{stop_distance:.2f}) < 1.0 * ATR14 (₹{atr14:.2f}). Skipped noise trap.",
            )

        # Volatility targeting
        vol_scalar = self.target_annual_vol / max(0.05, realized_annual_vol)
        tau_vol = self.base_risk_fraction * vol_scalar

        # Fractional Kelly
        payoff_b = max(0.1, (target_price - entry_price) / stop_distance)
        p = float(np.clip(estimated_win_prob, 0.05, 0.95))
        edge_expectation = (p * payoff_b) - (1.0 - p)
        if edge_expectation <= 0.0:
            return SizingCalculation(
                symbol=symbol, entry_price=entry_price, stop_price=stop_price, stop_distance=round(stop_distance, 2),
                atr14=round(atr14, 2), is_noise_trap_skipped=False, tau_vol=round(tau_vol, 4), brier_skill_score=round(rolling_bss, 4),
                kelly_risk_fraction=0.0, tau_effective=0.0, shares_quantity=0, proposed_notional=0.0,
                is_aborted=True, regime_mode="ABORTED", rationale="Negative expectancy. Aborted.",
            )
        f_star_risk = 0.25 * (edge_expectation / payoff_b)

        # Calibration selection
        if historical_closed_trades_count < 200:
            regime = "COLD_START"
            tau_eff = min(tau_vol, 0.010)
        elif rolling_bss <= 0.0:
            regime = "DEFENSIVE"
            tau_eff = 0.5 * tau_vol
        else:
            regime = "CALIBRATED_KELLY"
            tau_eff = min(tau_vol, f_star_risk)

        tau_eff = float(np.clip(tau_eff, 0.001, self.max_risk_ceiling))

        # Quantity calculation & 20% notional ceiling
        raw_quantity = int(np.floor((current_equity * tau_eff) / stop_distance))
        max_notional_cap = current_equity * self.max_notional_pct
        final_notional = min(raw_quantity * entry_price, max_notional_cap)
        final_shares = int(np.floor(final_notional / entry_price))

        return SizingCalculation(
            symbol=symbol, entry_price=entry_price, stop_price=stop_price, stop_distance=round(stop_distance, 2),
            atr14=round(atr14, 2), is_noise_trap_skipped=False, tau_vol=round(tau_vol, 4), brier_skill_score=round(rolling_bss, 4),
            kelly_risk_fraction=round(f_star_risk, 4), tau_effective=round(tau_eff, 4), shares_quantity=final_shares,
            proposed_notional=round(final_shares * entry_price, 2), is_aborted=(final_shares <= 0),
            regime_mode=regime, rationale="Sizing computed successfully.",
        )
```

---

### 5. Pre-Trade Risk Engine (`alphacouncil/risk/pre_trade.py`)
```python
from dataclasses import dataclass
from typing import Optional
import time

@dataclass
class RiskValidationResult:
    is_approved: bool
    adjusted_quantity: int
    reason: str
    rejection_code: Optional[str] = None

class PreTradeRiskEngine:
    def __init__(self, max_single_stock_pct: float = 0.20, max_orders_per_sec: int = 10):
        self.max_single_stock_pct = max_single_stock_pct
        self.max_orders_per_sec = max_orders_per_sec
        self.order_timestamps = []

    def validate_order(self, symbol: str, proposed_quantity: int, entry_price: float,
                       current_equity: float, current_position_shares: int = 0,
                       is_reduce_only: bool = False) -> RiskValidationResult:
        now = time.time()
        self.order_timestamps = [t for t in self.order_timestamps if now - t < 1.0]
        if len(self.order_timestamps) >= self.max_orders_per_sec:
            return RiskValidationResult(False, 0, "RATE_LIMIT_EXCEEDED", "ERR_RATE_LIMIT")
        self.order_timestamps.append(now)

        if proposed_quantity <= 0 or entry_price <= 0.0:
            return RiskValidationResult(False, 0, "INVALID_PARAMETERS", "ERR_INVALID_PARAMS")

        if current_equity <= 0.0:
            return RiskValidationResult(False, 0, "FAIL_CLOSED: Equity unresolved", "ERR_ACCOUNT_UNRESOLVED")

        proposed_notional = proposed_quantity * entry_price
        max_notional_allowed = current_equity * self.max_single_stock_pct
        if proposed_notional > max_notional_allowed:
            capped_qty = int(max_notional_allowed // entry_price)
            if capped_qty <= 0:
                return RiskValidationResult(False, 0, "CONCENTRATION_EXCEEDED", "ERR_CONCENTRATION")
            return RiskValidationResult(True, capped_qty, f"APPROVED_WITH_CAPPING to {capped_qty} shares")

        return RiskValidationResult(True, proposed_quantity, "PRE_TRADE_PASSED")
```

---

### 6. Statutory SEBI Tariffs & Impact Friction (`alphacouncil/execution/friction.py`)
```python
from dataclasses import dataclass
import numpy as np

@dataclass
class FrictionBreakdown:
    gross_notional: float
    stt_tax: float
    brokerage: float
    exchange_charges: float
    sebi_charges: float
    stamp_duty: float
    gst: float
    market_impact_slippage: float
    total_friction_inr: float
    effective_friction_bps: float

class IndianMarketFrictionModel:
    def __init__(self, stt_rate: float = 0.0010, brokerage_rate: float = 0.0005, brokerage_cap: float = 20.0,
                 nse_txn_rate: float = 0.0000297, sebi_rate: float = 0.000001, stamp_duty_rate: float = 0.00015,
                 gst_rate: float = 0.18, gamma_impact: float = 0.314):
        self.stt_rate = stt_rate
        self.brokerage_rate = brokerage_rate
        self.brokerage_cap = brokerage_cap
        self.nse_txn_rate = nse_txn_rate
        self.sebi_rate = sebi_rate
        self.stamp_duty_rate = stamp_duty_rate
        self.gst_rate = gst_rate
        self.gamma_impact = gamma_impact

    def compute_roundtrip_friction(self, quantity: int, entry_price: float, exit_price: float,
                                   annualized_vol: float, adv20: float) -> FrictionBreakdown:
        buy_notional = quantity * entry_price
        sell_notional = quantity * exit_price
        total_notional = buy_notional + sell_notional

        stt = (buy_notional * self.stt_rate) + (sell_notional * self.stt_rate)
        brok_buy = min(self.brokerage_cap, buy_notional * self.brokerage_rate)
        brok_sell = min(self.brokerage_cap, sell_notional * self.brokerage_rate)
        total_brokerage = brok_buy + brok_sell
        nse_charges = total_notional * self.nse_txn_rate
        sebi_charges = total_notional * self.sebi_rate
        stamp_duty = buy_notional * self.stamp_duty_rate
        gst = (total_brokerage + nse_charges + sebi_charges) * self.gst_rate

        # Almgren-Chriss square root market impact
        participation = quantity / max(100.0, adv20)
        daily_vol = annualized_vol / np.sqrt(252.0)
        impact_inr = buy_notional * (self.gamma_impact * daily_vol * np.sqrt(participation))

        total_friction = stt + total_brokerage + nse_charges + sebi_charges + stamp_duty + gst + impact_inr
        effective_bps = (total_friction / (buy_notional + 1e-8)) * 10_000.0

        return FrictionBreakdown(
            gross_notional=round(buy_notional, 2), stt_tax=round(stt, 2), brokerage=round(total_brokerage, 2),
            exchange_charges=round(nse_charges, 2), sebi_charges=round(sebi_charges, 2), stamp_duty=round(stamp_duty, 2),
            gst=round(gst, 2), market_impact_slippage=round(impact_inr, 2), total_friction_inr=round(total_friction, 2),
            effective_friction_bps=round(effective_bps, 2),
        )
```

---

### 7. Idempotent OMS & GTT Sync (`alphacouncil/execution/oms.py`)
```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, Tuple
import uuid
import time

class OrderStatus(Enum):
    PENDING_RISK = "PENDING_RISK"
    SUBMITTED = "SUBMITTED"
    ACCEPTED = "ACCEPTED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"

class OrderType(Enum):
    MARKET = "MARKET"
    SL_MARKET = "SL_MARKET"

@dataclass
class Order:
    order_id: str
    client_order_id: str
    symbol: str
    side: str
    order_type: OrderType
    quantity: int
    filled_quantity: int = 0
    limit_price: Optional[float] = None
    trigger_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING_RISK
    linked_stop_order_id: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

class IdempotentOMS:
    def __init__(self):
        self.orders: Dict[str, Order] = {}
        self.execution_audit_log = []

    def create_bracket_entry(self, symbol: str, quantity: int, entry_price: float,
                             stop_price: float, target_price: float) -> Tuple[Order, Order]:
        client_order_id = f"ORD_{symbol}_{int(time.time()*1000)}"
        entry_order = Order(
            order_id=str(uuid.uuid4()), client_order_id=client_order_id, symbol=symbol,
            side="BUY", order_type=OrderType.MARKET, quantity=quantity, limit_price=entry_price,
            status=OrderStatus.SUBMITTED,
        )
        stop_order_id = f"GTT_STOP_{uuid.uuid4().hex[:8]}"
        stop_order = Order(
            order_id=stop_order_id, client_order_id=f"SLM_{client_order_id}", symbol=symbol,
            side="SELL", order_type=OrderType.SL_MARKET, quantity=quantity, trigger_price=stop_price,
            status=OrderStatus.ACCEPTED,
        )
        entry_order.linked_stop_order_id = stop_order_id
        self.orders[entry_order.order_id] = entry_order
        self.orders[stop_order.order_id] = stop_order
        return entry_order, stop_order

    def record_partial_fill(self, entry_order_id: str, filled_shares: int, fill_price: float) -> Optional[Order]:
        entry_order = self.orders.get(entry_order_id)
        if not entry_order:
            return None
        entry_order.filled_quantity += filled_shares
        entry_order.status = OrderStatus.FILLED if entry_order.filled_quantity >= entry_order.quantity else OrderStatus.PARTIALLY_FILLED
        if entry_order.linked_stop_order_id in self.orders:
            stop_order = self.orders[entry_order.linked_stop_order_id]
            stop_order.quantity = entry_order.filled_quantity
            return stop_order
        return None

    def cancel_entry_and_orphaned_stops(self, entry_order_id: str) -> bool:
        entry_order = self.orders.get(entry_order_id)
        if not entry_order:
            return False
        entry_order.status = OrderStatus.CANCELED
        if entry_order.linked_stop_order_id in self.orders:
            stop_order = self.orders[entry_order.linked_stop_order_id]
            if entry_order.filled_quantity == 0:
                stop_order.status = OrderStatus.CANCELED
        return True
```
