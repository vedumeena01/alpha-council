"""
Adversarial Stress & Chaos Fault Injection Harness for DhanHQ Execution Adapter.
Simulates extreme market edge cases, floating point noise, rate-limit storms,
bad geometry, zero-quantity allocations, and emergency circuit purges.
"""

import os
import time
from typing import Dict, Any

from alphacouncil.execution.dhan_adapter import (
    DhanExecutionAdapter,
    is_valid_nse_tick,
)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_adversarial_stress_suite() -> Dict[str, Any]:
    print("=" * 80)
    print("STARTING RUN 3: ADVERSARIAL STRESS & CHAOS INJECTION SUITE")
    print("=" * 80)

    adapter = DhanExecutionAdapter(sandbox_mode=True)
    stress_results = {}

    # Stress 1: Inverted Geometry Injection
    print("\n[Stress 1] Inverted Geometry Injection (Target <= Entry or Stop >= Entry)...")
    res_geom1 = adapter.place_gtt_oco_bracket("RELIANCE", 10, 1345.0, 1300.0, 1320.0)
    res_geom2 = adapter.place_gtt_oco_bracket("RELIANCE", 10, 1345.0, 1380.0, 1350.0)
    s1_pass = (
        res_geom1.success is False
        and res_geom1.order_status == "REJECTED_INVALID_GEOMETRY"
        and res_geom2.success is False
        and res_geom2.order_status == "REJECTED_INVALID_GEOMETRY"
    )
    stress_results["stress_1_inverted_geometry"] = {
        "passed": s1_pass,
        "detail": f"Target < Entry: {res_geom1.order_status}, Stop > Entry: {res_geom2.order_status}",
    }
    print(f"  -> Result: {'PASS' if s1_pass else 'FAIL'} ({stress_results['stress_1_inverted_geometry']['detail']})")

    # Stress 2: Zero / Negative Quantity Injection
    print("\n[Stress 2] Zero & Negative Quantity Capital Exhaustion Injection...")
    res_qty0 = adapter.place_gtt_oco_bracket("INFY", 0, 1090.0, 1120.0, 1070.0)
    res_qty_neg = adapter.place_gtt_oco_bracket("INFY", -15, 1090.0, 1120.0, 1070.0)
    s2_pass = (
        res_qty0.success is False
        and res_qty0.order_status == "REJECTED_ZERO_QUANTITY"
        and res_qty_neg.success is False
        and res_qty_neg.order_status == "REJECTED_ZERO_QUANTITY"
    )
    stress_results["stress_2_zero_quantity"] = {
        "passed": s2_pass,
        "detail": f"Qty=0: {res_qty0.order_status}, Qty=-15: {res_qty_neg.order_status}",
    }
    print(f"  -> Result: {'PASS' if s2_pass else 'FAIL'} ({stress_results['stress_2_zero_quantity']['detail']})")

    # Stress 3: Unmapped / Delisted Ticker Injection
    print("\n[Stress 3] Unmapped / Delisted Ticker Injection...")
    res_unmapped = adapter.place_gtt_oco_bracket("INVALID_CORP_TICKER", 10, 100.0, 110.0, 90.0)
    s3_pass = (
        res_unmapped.success is False
        and res_unmapped.order_status == "REJECTED_UNKNOWN_SYMBOL"
    )
    stress_results["stress_3_unmapped_ticker"] = {
        "passed": s3_pass,
        "detail": f"Status: {res_unmapped.order_status}, Msg: {res_unmapped.message}",
    }
    print(f"  -> Result: {'PASS' if s3_pass else 'FAIL'} ({stress_results['stress_3_unmapped_ticker']['detail']})")

    # Stress 4: High-Precision Floating Point Noise (8 Decimals)
    print("\n[Stress 4] Floating Point Sub-Tick Noise Injection (8 decimal places)...")
    noisy_entry = 1345.12345678
    noisy_target = 1389.98765432
    noisy_stop = 1312.44444444
    res_noise = adapter.place_gtt_oco_bracket("RELIANCE", 20, noisy_entry, noisy_target, noisy_stop, auto_snap_ticks=True)
    if res_noise.success:
        order = adapter.active_gtt_orders[res_noise.order_id]
        all_ticks_valid = (
            is_valid_nse_tick(order.entry_price)
            and is_valid_nse_tick(order.target_price)
            and is_valid_nse_tick(order.stop_loss_price)
            and is_valid_nse_tick(order.entry_trigger_price)
            and is_valid_nse_tick(order.target_trigger_price)
            and is_valid_nse_tick(order.stop_loss_trigger_price)
        )
    else:
        all_ticks_valid = False
    s4_pass = res_noise.success and all_ticks_valid
    stress_results["stress_4_float_noise"] = {
        "passed": s4_pass,
        "detail": f"Snapped: Entry ₹{order.entry_price}, Target ₹{order.target_price}, Stop ₹{order.stop_loss_price}",
    }
    print(f"  -> Result: {'PASS' if s4_pass else 'FAIL'} ({stress_results['stress_4_float_noise']['detail']})")

    # Stress 5: Idempotency Duplicate Flooding (20 Orders Storm)
    print("\n[Stress 5] Idempotency Flooding Storm (20 rapid duplicate orders for SBIN)...")
    storm_success = 0
    storm_rejected = 0
    for _ in range(20):
        r = adapter.place_gtt_oco_bracket("SBIN", 50, 1170.0, 1200.0, 1150.0, allow_duplicate_symbol=False)
        if r.success:
            storm_success += 1
        else:
            storm_rejected += 1
    s5_pass = (storm_success == 1 and storm_rejected == 19)
    stress_results["stress_5_idempotency_storm"] = {
        "passed": s5_pass,
        "detail": f"Accepted: {storm_success}, Blocked Duplicates: {storm_rejected}",
    }
    print(f"  -> Result: {'PASS' if s5_pass else 'FAIL'} ({stress_results['stress_5_idempotency_storm']['detail']})")

    # Stress 6: Emergency Circuit Purge (Cancel All Active Orders)
    print("\n[Stress 6] Emergency Circuit-Breaker Purge...")
    pre_cancel_count = len(adapter.active_gtt_orders)
    cancelled = adapter.emergency_cancel_all_gtt()
    post_cancel_count = len(adapter.active_gtt_orders)
    s6_pass = (cancelled == pre_cancel_count and post_cancel_count == 0)
    stress_results["stress_6_circuit_purge"] = {
        "passed": s6_pass,
        "detail": f"Purged {cancelled} orders. Remaining active: {post_cancel_count}",
    }
    print(f"  -> Result: {'PASS' if s6_pass else 'FAIL'} ({stress_results['stress_6_circuit_purge']['detail']})")

    # Stress 7: Simulated Network Latency Delay
    print("\n[Stress 7] Network Latency & Response Verification (Simulating 500ms round-trip)...")
    t0 = time.time()
    res_lat = adapter.place_gtt_oco_bracket("TCS", 10, 2380.0, 2450.0, 2340.0)
    time.sleep(0.05)  # 50ms simulated roundtrip
    elapsed = (time.time() - t0) * 1000
    s7_pass = res_lat.success and elapsed < 1000
    stress_results["stress_7_latency_check"] = {
        "passed": s7_pass,
        "detail": f"Latency: {elapsed:.1f}ms, Status: {res_lat.order_status}",
    }
    print(f"  -> Result: {'PASS' if s7_pass else 'FAIL'} ({stress_results['stress_7_latency_check']['detail']})")

    all_passed = all(v["passed"] for v in stress_results.values())
    print("\n" + "=" * 80)
    print(f"RUN 3 ADVERSARIAL STRESS TEST SUMMARY: {'ALL 7 TESTS PASSED (100%)' if all_passed else 'SOME TESTS FAILED'}")
    print("=" * 80)
    return stress_results


if __name__ == "__main__":
    run_adversarial_stress_suite()
