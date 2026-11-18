"""
Statutory SEBI (Oct 1, 2024 Circular) Fee Schedule & Almgren-Chriss Market Impact Model.
Provides verified transaction friction calculation for NSE cash delivery and intraday legs.
"""

from dataclasses import dataclass
import numpy as np


@dataclass
class FrictionBreakdown:
    """Itemized breakdown of all statutory fees and market impact."""
    gross_notional: float
    stt_tax: float
    brokerage: float
    exchange_charges: float
    sebi_charges: float
    stamp_duty: float
    gst: float
    dp_charges: float
    market_impact_slippage: float
    total_friction_inr: float
    effective_friction_bps: float


class IndianMarketFrictionModel:
    """
    Computes statutory NSE fees, depository charges, and non-linear market impact.
    Reflects the SEBI True-to-Label circular effective October 1, 2024.
    """

    def __init__(
        self,
        stt_rate: float = 0.0010,           # 0.10% buy & sell delivery
        brokerage_rate: float = 0.0005,      # 0.05%
        brokerage_cap: float = 20.0,         # ₹20 flat cap
        nse_txn_rate: float = 0.0000297,     # 0.00297% revised NSE charge
        sebi_rate: float = 0.000001,         # ₹10 / Cr (0.0001%)
        stamp_duty_rate: float = 0.00015,    # 0.015% buy only
        gst_rate: float = 0.18,              # 18% on fees
        dp_charge_per_debit: float = 15.93,  # CDSL/NSDL depository debit charge
        gamma_impact: float = 0.314,         # Square-root impact parameter
        max_adv_participation: float = 0.025 # 2.5% ADV cap
    ):
        self.stt_rate = stt_rate
        self.brokerage_rate = brokerage_rate
        self.brokerage_cap = brokerage_cap
        self.nse_txn_rate = nse_txn_rate
        self.sebi_rate = sebi_rate
        self.stamp_duty_rate = stamp_duty_rate
        self.gst_rate = gst_rate
        self.dp_charge_per_debit = dp_charge_per_debit
        self.gamma_impact = gamma_impact
        self.max_adv_participation = max_adv_participation

    def compute_roundtrip_friction(
        self,
        quantity: int,
        entry_price: float,
        exit_price: float,
        annualized_vol: float,
        adv20: float,
        is_intraday: bool = False,
    ) -> FrictionBreakdown:
        """
        Computes complete round-trip transaction costs across both Entry (Buy) and Exit (Sell) legs.
        Includes round-trip Almgren-Chriss impact and CDSL/NSDL DP debit charges for delivery.
        """
        buy_notional = quantity * entry_price
        sell_notional = quantity * exit_price
        total_notional = buy_notional + sell_notional

        # 1. Securities Transaction Tax (STT)
        if is_intraday:
            stt = sell_notional * 0.00025  # 0.025% on intraday equity sell
        else:
            stt = (buy_notional * self.stt_rate) + (sell_notional * self.stt_rate)  # 0.10% each leg

        # 2. Brokerage: min(0.05%, ₹20) per order
        brok_buy = min(self.brokerage_cap, buy_notional * self.brokerage_rate)
        brok_sell = min(self.brokerage_cap, sell_notional * self.brokerage_rate)
        total_brokerage = brok_buy + brok_sell

        # 3. Exchange Turnover Charges (NSE 0.00297%)
        nse_charges = total_notional * self.nse_txn_rate

        # 4. SEBI Turnover Charges (0.0001%)
        sebi_charges = total_notional * self.sebi_rate

        # 5. Stamp Duty (Buy leg only)
        if is_intraday:
            stamp_duty = buy_notional * 0.00003  # 0.003% intraday
        else:
            stamp_duty = buy_notional * self.stamp_duty_rate  # 0.015% delivery

        # 6. GST: 18% on (Brokerage + Exchange Charges + SEBI Charges)
        taxable_services = total_brokerage + nse_charges + sebi_charges
        gst = taxable_services * self.gst_rate

        # 7. Depository (DP) Debit Charge: ₹15.93 per delivery sell transaction (0 for intraday)
        dp_cost = 0.0 if is_intraday else self.dp_charge_per_debit

        # 8. Non-Linear Almgren-Chriss Square-Root Market Impact (Applied on Both Entry & Exit Legs)
        participation = quantity / max(100.0, adv20)
        daily_vol = annualized_vol / np.sqrt(252.0)
        impact_pct = self.gamma_impact * daily_vol * np.sqrt(participation)
        market_impact_inr = total_notional * impact_pct

        total_friction = stt + total_brokerage + nse_charges + sebi_charges + stamp_duty + gst + dp_cost + market_impact_inr
        effective_bps = (total_friction / (buy_notional + 1e-8)) * 10_000.0

        return FrictionBreakdown(
            gross_notional=round(buy_notional, 2),
            stt_tax=round(stt, 2),
            brokerage=round(total_brokerage, 2),
            exchange_charges=round(nse_charges, 2),
            sebi_charges=round(sebi_charges, 2),
            stamp_duty=round(stamp_duty, 2),
            gst=round(gst, 2),
            dp_charges=round(dp_cost, 2),
            market_impact_slippage=round(market_impact_inr, 2),
            total_friction_inr=round(total_friction, 2),
            effective_friction_bps=round(effective_bps, 2),
        )
