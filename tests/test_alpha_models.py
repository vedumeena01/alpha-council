"""
Unit Tests for Triple Barrier Method, OU Half-Life, and FinBERT Contamination Probe.
"""

import numpy as np
from alphacouncil.alpha.triple_barrier import TripleBarrierLabeler
from alphacouncil.alpha.sentiment_nlp import FinBertSentimentExtractor


def test_triple_barrier_stop_loss_hit():
    labeler = TripleBarrierLabeler(payoff_ratio=2.0, max_vertical_days=5)

    # Entry at 100, Stop at 90 -> d_stop = 10, target = 120
    forward_lows = np.array([98.0, 95.0, 89.0, 95.0, 96.0])  # Hits 89.0 on day 3
    forward_highs = np.array([102.0, 103.0, 101.0, 104.0, 105.0])
    forward_closes = np.array([100.0, 99.0, 90.0, 96.0, 97.0])
    recent_prices = np.array([98.0, 99.0, 100.0, 101.0, 100.0] * 5)

    outcome = labeler.evaluate_path(
        entry_price=100.0,
        stop_price=90.0,
        forward_highs=forward_highs,
        forward_lows=forward_lows,
        forward_closes=forward_closes,
        recent_prices=recent_prices,
    )

    assert outcome.barrier_hit == "LOWER"
    assert not outcome.is_success
    assert outcome.exit_price == 90.0
    assert outcome.realized_return_pct == -0.10


def test_triple_barrier_take_profit_hit():
    labeler = TripleBarrierLabeler(payoff_ratio=2.0, max_vertical_days=5)

    forward_lows = np.array([98.0, 99.0, 100.0, 102.0, 103.0])
    forward_highs = np.array([102.0, 108.0, 122.0, 125.0, 128.0])  # Hits 122.0 on day 3 (target 120)
    forward_closes = np.array([101.0, 106.0, 121.0, 123.0, 126.0])
    recent_prices = np.array([98.0, 99.0, 100.0, 101.0, 100.0] * 5)

    outcome = labeler.evaluate_path(
        entry_price=100.0,
        stop_price=90.0,
        forward_highs=forward_highs,
        forward_lows=forward_lows,
        forward_closes=forward_closes,
        recent_prices=recent_prices,
    )

    assert outcome.barrier_hit == "UPPER"
    assert outcome.is_success
    assert outcome.exit_price == 120.0
    assert outcome.realized_return_pct == 0.20


def test_finbert_sentiment_and_anonymization():
    extractor = FinBertSentimentExtractor()
    pos_score = extractor.extract_sentiment(
        "RELIANCE", "Record EBITDA growth and massive margin expansion across units"
    )
    assert pos_score > 0.0

    neg_score = extractor.extract_sentiment(
        "INFY", "Significant margin contraction and customer litigation risk"
    )
    assert neg_score < 0.0

    # Synthetic anonymization
    synth_sym, idxs, rebased = extractor.anonymize_series(
        "RELIANCE", ["2025-01-01", "2025-01-02"], [2000.0, 2100.0]
    )
    assert synth_sym.startswith("SYNTH_")
    assert idxs == [0, 1]
    assert rebased == [100.0, 105.0]
