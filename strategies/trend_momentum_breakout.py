"""
FATE QUANT V1 — Deterministic Trend + Momentum + Breakout Strategy
Long-only for V1.

A trade becomes eligible only when ALL conditions pass.
Default state remains NO TRADE.
"""

from dataclasses import dataclass
from typing import Optional
import pandas as pd
import numpy as np


@dataclass
class SignalResult:
    symbol: str
    side: str                          # "long" only in V1
    entry_price: float
    stop_price: float
    score: float
    reason: str
    is_valid: bool


class TrendMomentumBreakout:
    """
    Deterministic rules (no ML / no AI).

    Higher timeframe (4h): trend filter
    Primary timeframe (1h): entry logic
    """

    def __init__(self, higher_tf_df: pd.DataFrame, primary_tf_df: pd.DataFrame):
        self.htf = higher_tf_df.copy()
        self.ptf = primary_tf_df.copy()
        self._prepare()

    def _prepare(self):
        # Simple moving averages for trend
        self.htf["sma_50"] = self.htf["close"].rolling(50).mean()
        self.htf["sma_200"] = self.htf["close"].rolling(200).mean()

        # Momentum
        self.ptf["roc_10"] = self.ptf["close"].pct_change(10)
        self.ptf["sma_20"] = self.ptf["close"].rolling(20).mean()
        self.ptf["sma_50"] = self.ptf["close"].rolling(50).mean()

        # Volatility (ATR proxy)
        self.ptf["tr"] = np.maximum(
            self.ptf["high"] - self.ptf["low"],
            np.maximum(
                abs(self.ptf["high"] - self.ptf["close"].shift()),
                abs(self.ptf["low"] - self.ptf["close"].shift()),
            ),
        )
        self.ptf["atr_14"] = self.ptf["tr"].rolling(14).mean()

        # Volume
        self.ptf["vol_sma_20"] = self.ptf["volume"].rolling(20).mean()

    def generate_signal(self, symbol: str) -> SignalResult:
        """
        Returns a SignalResult. is_valid=True only if all conditions pass.
        """
        if len(self.htf) < 200 or len(self.ptf) < 50:
            return SignalResult(symbol, "long", 0, 0, 0, "Insufficient data", False)

        # 1. Higher-timeframe trend must be bullish
        htf_bullish = (
            self.htf["close"].iloc[-1] > self.htf["sma_50"].iloc[-1]
            and self.htf["sma_50"].iloc[-1] > self.htf["sma_200"].iloc[-1]
        )
        if not htf_bullish:
            return SignalResult(symbol, "long", 0, 0, 0, "HTF trend not bullish", False)

        # 2. Momentum agrees
        momentum_ok = (
            self.ptf["roc_10"].iloc[-1] > 0
            and self.ptf["close"].iloc[-1] > self.ptf["sma_20"].iloc[-1]
        )
        if not momentum_ok:
            return SignalResult(symbol, "long", 0, 0, 0, "Momentum not aligned", False)

        # 3. Simple structure break (close above recent high)
        lookback = 20
        recent_high = self.ptf["high"].iloc[-lookback:-1].max()
        structure_break = self.ptf["close"].iloc[-1] > recent_high
        if not structure_break:
            return SignalResult(symbol, "long", 0, 0, 0, "No structure break", False)

        # 4. Volume confirmation
        volume_ok = self.ptf["volume"].iloc[-1] > self.ptf["vol_sma_20"].iloc[-1] * 1.2
        if not volume_ok:
            return SignalResult(symbol, "long", 0, 0, 0, "Volume not confirming", False)

        # 5. Volatility within bounds (not too quiet, not exploding)
        atr = self.ptf["atr_14"].iloc[-1]
        atr_pct = atr / self.ptf["close"].iloc[-1]
        if atr_pct < 0.005 or atr_pct > 0.05:
            return SignalResult(symbol, "long", 0, 0, 0, "Volatility out of bounds", False)

        # Entry and stop
        entry = self.ptf["close"].iloc[-1]
        stop = entry - (atr * 1.5)          # 1.5 ATR stop

        # Simple score (will be expanded later with full weighted model)
        score = 82.0  # Placeholder — all conditions passed = valid zone

        return SignalResult(
            symbol=symbol,
            side="long",
            entry_price=entry,
            stop_price=stop,
            score=score,
            reason="All V1 conditions passed",
            is_valid=True,
        )
