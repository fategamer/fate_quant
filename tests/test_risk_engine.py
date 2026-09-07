from risk.risk_engine import RiskEngine


def test_position_size_respects_risk_budget():
    engine = RiskEngine(equity=10_000, research_mode=True)
    result = engine.calculate_position_size(entry_price=100.0, stop_price=99.0)
    assert not result.rejected
    # risk = 25, stop distance = 1 → qty = 25
    assert abs(result.quantity - 25.0) < 1e-9
    assert abs(result.risk_amount - 25.0) < 1e-9


def test_zero_stop_rejected():
    engine = RiskEngine(equity=10_000, research_mode=True)
    result = engine.calculate_position_size(entry_price=100.0, stop_price=100.0)
    assert result.rejected


def test_live_trading_blocked_outside_research():
    engine = RiskEngine(equity=10_000, research_mode=False)
    result = engine.calculate_position_size(entry_price=100.0, stop_price=99.0)
    assert result.rejected


def test_drawdown_kill_switch():
    engine = RiskEngine(equity=10_000, research_mode=True)
    engine.update_equity(9_400)  # 6% from peak > 5%
    assert engine.check_kill_switch() is True
    assert engine.is_locked
