"""
7-Model Orthogonal Ablation Suite & Benchmark Comparison Harness.
Codifies Section 8 of RFC v5.0, proving whether empirical alpha originates from
the quantitative core (H1), the NLP sentiment factor (H2), or the risk engine.
"""

from typing import Dict, List
from alphacouncil.data.feed import Bar
from alphacouncil.backtest.engine import BacktestEngine, BacktestResult


class AblationSuiteRunner:
    """
    Executes the 7 ablation configurations and passive benchmarks across the exact same dataset.
    """

    def __init__(self, n_trials_logged: int = 150):
        self.n_trials_logged = n_trials_logged

    def run_full_suite(
        self, universe_data: Dict[str, List[Bar]]
    ) -> Dict[str, BacktestResult]:
        """
        Runs all 7 ablation models sequentially.
        """
        results: Dict[str, BacktestResult] = {}

        # 1. alpha_Null: Random Coin Flip + Vol-Targeting (Isolates pure sizing contribution)
        eng_null = BacktestEngine(
            use_sweep_signal=False,
            random_entry=True,
            use_vol_sizing=True,
            use_kelly_cap=False,
            use_sentiment_nlp=False,
            use_pit_filter=False,
            use_atr_stop=False,
        )
        results["alpha_Null"] = eng_null.run(
            universe_data, config_name="α_Null (Random Coin Flip)", n_trials=self.n_trials_logged
        )

        # 2. alpha_Null_Time: Random Entry at Sweep Timing (Isolates filter vs signal alpha)
        eng_null_time = BacktestEngine(
            use_sweep_signal=False,
            random_entry=True,
            use_vol_sizing=True,
            use_kelly_cap=False,
            use_sentiment_nlp=False,
            use_pit_filter=True,
            use_atr_stop=False,
        )
        results["alpha_Null_Time"] = eng_null_time.run(
            universe_data, config_name="α_Null+Time (Random + Filter)", n_trials=self.n_trials_logged
        )

        # 3. alpha_Null_SMC: Random Entry + ATR Invalidation Stop (Tests stop loss edge alone)
        eng_null_smc = BacktestEngine(
            use_sweep_signal=False,
            random_entry=True,
            use_vol_sizing=True,
            use_kelly_cap=False,
            use_sentiment_nlp=False,
            use_pit_filter=False,
            use_atr_stop=True,
        )
        results["alpha_Null_SMC"] = eng_null_smc.run(
            universe_data, config_name="α_Null+SMC (Random + ATR Stop)", n_trials=self.n_trials_logged
        )

        # 4. alpha_Tech: Baseline Sweep Signal Alone ($H_1$) + Fixed 1% Risk
        eng_tech = BacktestEngine(
            use_sweep_signal=True,
            random_entry=False,
            use_vol_sizing=False,
            use_kelly_cap=False,
            use_sentiment_nlp=False,
            use_pit_filter=False,
            use_atr_stop=False,
        )
        results["alpha_Tech"] = eng_tech.run(
            universe_data, config_name="α_Tech (Sweep Signal Alone)", n_trials=self.n_trials_logged
        )

        # 5. alpha_Tech_Risk: Sweep Detector ($H_1$) + Vol-Targeting + ATR Stops
        eng_tech_risk = BacktestEngine(
            use_sweep_signal=True,
            random_entry=False,
            use_vol_sizing=True,
            use_kelly_cap=False,
            use_sentiment_nlp=False,
            use_pit_filter=False,
            use_atr_stop=True,
        )
        results["alpha_Tech_Risk"] = eng_tech_risk.run(
            universe_data, config_name="α_Tech+Risk (Sweep + Vol-Risk)", n_trials=self.n_trials_logged
        )

        # 6. alpha_Tech_Fund: Sweep Detector ($H_1$) + Point-in-Time Fundamental Screening
        eng_tech_fund = BacktestEngine(
            use_sweep_signal=True,
            random_entry=False,
            use_vol_sizing=True,
            use_kelly_cap=False,
            use_sentiment_nlp=False,
            use_pit_filter=True,
            use_atr_stop=True,
        )
        results["alpha_Tech_Fund"] = eng_tech_fund.run(
            universe_data, config_name="α_Tech+Fund (Sweep + PIT Filter)", n_trials=self.n_trials_logged
        )

        # 7. alpha_Council: Full Integrated Institutional System (H1 + H2 + Meta-Labeling + Kelly)
        eng_council = BacktestEngine(
            use_sweep_signal=True,
            random_entry=False,
            use_vol_sizing=True,
            use_kelly_cap=True,
            use_sentiment_nlp=True,
            use_pit_filter=True,
            use_atr_stop=True,
        )
        results["alpha_Council"] = eng_council.run(
            universe_data, config_name="α_Council (Full System RFC v5.0)", n_trials=self.n_trials_logged
        )

        return results
