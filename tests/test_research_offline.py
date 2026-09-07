import numpy as np
import pandas as pd
from backtesting.research_engine import ResearchEngine


def _ohlcv(n=300, start=100.0, drift=0.002):
    idx = pd.date_range("2024-01-01", periods=n, freq="h")
    close = start * np.cumprod(1 + np.linspace(drift, drift, n))
    high = close * 1.01
    low = close * 0.99
    open_ = close
    volume = np.full(n, 1000.0)
    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": volume},
        index=idx,
    )


def test_research_engine_runs_offline():
    ptf = _ohlcv()
    htf = ptf.resample("4h").agg({
        "open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"
    }).dropna()
    engine = ResearchEngine(initial_capital=10_000)
    report = engine.run_bar_by_bar("BTC/USDT", htf, ptf)
    assert report.final_equity > 0
    assert report.max_drawdown_pct < 100
