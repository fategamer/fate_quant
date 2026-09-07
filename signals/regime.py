"""
FATE QUANT — Regime Engine
Separate module. Does not place trades.
"""

from dataclasses import dataclass
import pandas as pd


@dataclass
class RegimeResult:
    label: str          # bull / bear / range / unknown
    score: float        # 0-100 contribution before weight
    reason: str


class RegimeEngine:
    def evaluate(self, htf: pd.DataFrame) -> RegimeResult:
        if htf is None or len(htf) < 210:
            return RegimeResult("unknown", 0.0, "Insufficient HTF data")

        close = htf["close"].iloc[-1]
        sma50 = htf["close"].rolling(50).mean().iloc[-1]
        sma200 = htf["close"].rolling(200).mean().iloc[-1]

        if pd.isna(sma50) or pd.isna(sma200):
            return RegimeResult("unknown", 0.0, "HTF MAs not ready")

        if close > sma50 > sma200:
            return RegimeResult("bull", 90.0, "Price > SMA50 > SMA200")
        if close < sma50 < sma200:
            return RegimeResult("bear", 20.0, "Price < SMA50 < SMA200")
        return RegimeResult("range", 45.0, "No clear HTF trend")
