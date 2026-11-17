"""
Marcos López de Prado Meta-Labeler & Council Reasoning Protocol.
AFML Chapter 3: Secondary model predicts probability of success and modulates
position sizing factor alpha_scale in [0.0, 1.0].
"""

from dataclasses import dataclass
import numpy as np


@dataclass
class MetaLabelOutput:
    """Output from the secondary Meta-Labeling model."""
    symbol: str
    primary_direction: int  # +1 (Long)
    predicted_win_prob: float
    alpha_scale: float  # In [0.0, 1.0] (One-way downscale valve)
    sentiment_score: float
    reasoning: str


class LopezDePradoMetaLabeler:
    """
    Implements Marcos López de Prado's Meta-Labeling secondary sizing model.
    Principle: Primary model decides direction (+1).
    Meta-model decides whether to take the bet and scales the bet size (alpha_scale).
    """

    def __init__(self, base_prior_win_rate: float = 0.52):
        self.base_prior_win_rate = base_prior_win_rate

    def evaluate_setup(
        self,
        symbol: str,
        sweep_signal: int,
        sentiment_score: float,
        rvol: float,
        price_above_50sma: bool,
        is_earnings_imminent: bool = False,
    ) -> MetaLabelOutput:
        """
        Combines microstructure factors and NLP sentiment to compute win probability
        and position scaling multiplier alpha_scale in [0.0, 1.0].
        """
        if sweep_signal <= 0:
            return MetaLabelOutput(
                symbol=symbol,
                primary_direction=0,
                predicted_win_prob=0.0,
                alpha_scale=0.0,
                sentiment_score=sentiment_score,
                reasoning="No primary sweep signal present.",
            )

        # 1. Hard Event Veto: Earnings within 24 hours
        if is_earnings_imminent:
            return MetaLabelOutput(
                symbol=symbol,
                primary_direction=sweep_signal,
                predicted_win_prob=0.30,
                alpha_scale=0.0,
                sentiment_score=sentiment_score,
                reasoning="HARD_VETO: Scheduled corporate earnings within 24h. 100% liquidation policy.",
            )

        # 2. Probability Modulation via Logistic/Score Synthesis
        prob = self.base_prior_win_rate

        # Sentiment factor contribution (H2 orthogonal signal)
        prob += sentiment_score * 0.08

        # Microstructure volume confirmation contribution
        if rvol >= 2.0:
            prob += 0.05
        elif rvol < 1.3:
            prob -= 0.04

        # Macro trend alignment contribution
        if price_above_50sma:
            prob += 0.03
        else:
            prob -= 0.03

        # Bound probability strictly in realistic quant range [0.35, 0.72]
        prob = float(np.clip(prob, 0.35, 0.72))

        # 3. Derive López de Prado Meta-Labeling Sizing Multiplier (alpha_scale)
        # Using sigmoid-like transformation centered at 0.50
        if prob <= 0.48:
            alpha_scale = 0.0  # Meta-model rejects trade
            reason = f"META_REJECTED: Win probability ({prob*100:.1f}%) below hurdle (48%)."
        elif prob <= 0.54:
            alpha_scale = 0.50  # Half size
            reason = f"META_DOWNSCALED: Marginal edge ({prob*100:.1f}%). Sizing scaled down to 50%."
        else:
            alpha_scale = 1.0  # Full size
            reason = f"META_APPROVED: Strong orthogonal signal ({prob*100:.1f}% win prob). Full size."

        return MetaLabelOutput(
            symbol=symbol,
            primary_direction=sweep_signal,
            predicted_win_prob=round(prob, 4),
            alpha_scale=alpha_scale,
            sentiment_score=round(sentiment_score, 4),
            reasoning=reason,
        )
