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
        # Higher timeframe trend
        self.htf["sma_50"] = self.htf["close"].rolling(50).mean()
        self.htf["sma_200"] = self.htf["close"].rolling(200).mean()

        # Primary timeframe
        self.ptf["roc_10"] = self.ptf["close"].pct_change(10)
        self.ptf["sma_20"] = self.ptf["close"].rolling(20).mean()
        self.ptf["sma_50"] = self.ptf["close"].rolling(50).mean()

        # ATR
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

        # Simple structure
        self.ptf["recent_high_20"] = self.ptf["high"].rolling(20).max().shift(1)

    def generate_signal(self, symbol: str) -> SignalResult:
        """
        Returns a SignalResult. is_valid=True only if all conditions pass.
        """
        if len(self.htf) < 210 or len(self.ptf) < 60:
            return SignalResult(symbol, "long", 0, 0, 0.0, "Insufficient data", False)

        # 1. Higher-timeframe trend must be bullish
        htf_close = self.htf["close"].iloc[-1]
        htf_sma50 = self.htf["sma_50"].iloc[-1]
        htf_sma200 = self.htf["sma_200"].iloc[-1]

        if pd.isna(htf_sma50) or pd.isna(htf_sma200):
            return SignalResult(symbol, "long", 0, 0, 0.0, "HTF indicators not ready", False)

        htf_bullish = htf_close > htf_sma50 and htf_sma50 > htf_sma200
        if not htf_bullish:
            return SignalResult(symbol, "long", 0, 0, 0.0, "HTF trend not bullish", False)

        # 2. Momentum agrees
        roc = self.ptf["roc_10"].iloc[-1]
        close = self.ptf["close"].iloc[-1]
        sma20 = self.ptf["sma_20"].iloc[-1]

        if pd.isna(roc) or pd.isna(sma20):
            return SignalResult(symbol, "long", 0, 0, 0.0, "Momentum indicators not ready", False)

        momentum_ok = roc > 0 and close > sma20
        if not momentum_ok:
            return SignalResult(symbol, "long", 0, 0, 0.0, "Momentum not aligned", False)

        # 3. Structure break
        recent_high = self.ptf["recent_high_20"].iloc[-1]
        if pd.isna(recent_high):
            return SignalResult(symbol, "long", 0, 0, 0.0, "Structure not ready", False)

        structure_break = close > recent_high
        if not structure_break:
            return SignalResult(symbol, "long", 0, 0, 0.0, "No structure break", False)

        # 4. Volume confirmation
        vol = self.ptf["volume"].iloc[-1]
        vol_sma = self.ptf["vol_sma_20"].iloc[-1]
        if pd.isna(vol_sma) or vol_sma == 0:
            return SignalResult(symbol, "long", 0, 0, 0.0, "Volume data invalid", False)

        volume_ok = vol > vol_sma * 1.15
        if not volume_ok:
            return SignalResult(symbol, "long", 0, 0, 0.0, "Volume not confirming", False)

        # 5. Volatility bounds
        atr = self.ptf["atr_14"].iloc[-1]
        if pd.isna(atr) or atr <= 0:
            return SignalResult(symbol, "long", 0, 0, 0.0, "ATR invalid", False)

        atr_pct = atr / close
        if atr_pct < 0.004 or atr_pct > 0.06:
            return SignalResult(symbol, "long", 0, 0, 0.0, "Volatility out of bounds", False)

        # Entry & Stop
        entry = close
        stop = entry - (atr * 1.5)

        # Basic score (all conditions passed → valid zone)
        # Later we will expand to full weighted model
        score = 85.0

        return SignalResult(
            symbol=symbol,
            side="long",
            entry_price=float(entry),
            stop_price=float(stop),
            score=score,
            reason="All V1 conditions passed",
            is_valid=True,
        )
