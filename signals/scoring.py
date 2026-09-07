"""
FATE QUANT — Weighted scoring
Weights live in config. This module only combines component scores.
"""

from typing import Dict
from config.settings import SCORE_WEIGHTS, SCORE_GATES


def combine_scores(components: Dict[str, float]) -> float:
    total = 0.0
    for name, weight in SCORE_WEIGHTS.items():
        total += float(components.get(name, 0.0)) * weight
    return max(0.0, min(100.0, total))


def gate(score: float) -> str:
    if score <= SCORE_GATES["no_trade_max"]:
        return "NO_TRADE"
    if score <= SCORE_GATES["watch_max"]:
        return "WATCH"
    if score < SCORE_GATES["high_confidence_min"]:
        return "VALID"
    return "HIGH_CONFIDENCE"
