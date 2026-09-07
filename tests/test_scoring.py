from signals.scoring import combine_scores, gate
from config.settings import SCORE_WEIGHTS


def test_weights_sum_to_one():
    assert abs(sum(SCORE_WEIGHTS.values()) - 1.0) < 1e-9


def test_perfect_components_near_100():
    components = {k: 100.0 for k in SCORE_WEIGHTS}
    assert abs(combine_scores(components) - 100.0) < 1e-9


def test_zero_components_is_zero():
    components = {k: 0.0 for k in SCORE_WEIGHTS}
    assert combine_scores(components) == 0.0


def test_gates():
    assert gate(50) == "NO_TRADE"
    assert gate(75) == "WATCH"
    assert gate(85) == "VALID"
    assert gate(95) == "HIGH_CONFIDENCE"
