"""
Unit Tests for Statutory SEBI Friction Schedule (Oct 1, 2024 Circular) and Market Impact.
"""

from alphacouncil.execution.friction import IndianMarketFrictionModel


def test_statutory_friction_exact_calculation():
    model = IndianMarketFrictionModel()

    # Buy 100 shares at ₹2,000 (Notional ₹200,000)
    # Sell 100 shares at ₹2,100 (Notional ₹210,000)
    # Total notional = ₹410,000
    friction = model.compute_roundtrip_friction(
        quantity=100,
        entry_price=2000.0,
        exit_price=2100.0,
        annualized_vol=0.20,
        adv20=1_000_000.0,
    )

    # 1. STT = (200,000 * 0.001) + (210,000 * 0.001) = 200 + 210 = ₹410.0
    assert friction.stt_tax == 410.0

    # 2. Brokerage = ₹20 buy + ₹20 sell = ₹40.0
    assert friction.brokerage == 40.0

    # 3. NSE Turnover = 410,000 * 0.0000297 = ₹12.18
    assert friction.exchange_charges == 12.18

    # 4. SEBI Turnover = 410,000 * 0.000001 = ₹0.41
    assert friction.sebi_charges == 0.41

    # 5. Stamp Duty = 200,000 * 0.00015 = ₹30.0 (Buy side only)
    assert friction.stamp_duty == 30.0

    # 6. GST = 18% of (40.0 + 12.18 + 0.41) = 18% of 52.59 = ₹9.47
    assert friction.gst == 9.47

    # Total statutory fee sum without impact:
    statutory_sum = 410.0 + 40.0 + 12.18 + 0.41 + 30.0 + 9.47
    assert friction.total_friction_inr >= statutory_sum
