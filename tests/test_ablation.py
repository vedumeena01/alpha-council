"""
Integration Tests for 7-Model Orthogonal Ablation Suite.
"""

from alphacouncil.data.feed import MarketDataFeed
from alphacouncil.backtest.ablation import AblationSuiteRunner


def test_ablation_suite_full_execution():
    feed = MarketDataFeed(seed=42)
    # 2 symbols, 100 bars for fast test execution
    market_data = feed.get_multi_symbol_universe(["RELIANCE", "INFY"], n_bars=100)

    runner = AblationSuiteRunner(n_trials_logged=50)
    results = runner.run_full_suite(market_data)

    assert len(results) == 7
    expected_configs = [
        "alpha_Null", "alpha_Null_Time", "alpha_Null_SMC",
        "alpha_Tech", "alpha_Tech_Risk", "alpha_Tech_Fund", "alpha_Council"
    ]
    for cfg in expected_configs:
        assert cfg in results
        res = results[cfg]
        assert len(res.equity_curve) > 0
        assert res.metrics.sharpe_ratio is not None
        assert 0.0 <= res.metrics.deflated_sharpe_ratio <= 1.0
