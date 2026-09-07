"""
FATE QUANT V1 — Deterministic Trend + Momentum + Breakout
Long-only. No look-ahead: evaluate a specific bar index, not the future last bar.
"""

from dataclasses import dataclass
import pandas as pd
import numpy as np

from signals.regime import RegimeEngine
from signals.scoring import combine_scores, gate


@dataclass
class SignalResult:
    symbol: str
    side: str
    entry_price: float
    stop_price: float
    score: float
    reason: str
    is_valid: bool
    gate: str = "NO_TRADE"


class TrendMomentumBreakout:
    def __init__(self, higher_tf_df: pd.DataFrame, primary_tf_df: pd.DataFrame):
        self.htf = higher_tf_df.copy()
        self.ptf = primary_tf_df.copy()
        self.regime = RegimeEngine()
        self._prepare()

    def _prepare(self):
        self.htf["sma_50"] = self.htf["close"].rolling(50).mean()
        self.htf["sma_200"] = self.htf["close"].rolling(200).mean()

        self.ptf["roc_10"] = self.ptf["close"].pct_change(10)
        self.ptf["sma_20"] = self.ptf["close"].rolling(20).mean()
        self.ptf["sma_50"] = self.ptf["close"].rolling(50).mean()

        prev_close = self.ptf["close"].shift()
        self.ptf["tr"] = np.maximum(
            self.ptf["high"] - self.ptf["low"],
            np.maximum(
                (self.ptf["high"] - prev_close).abs(),
                (self.ptf["low"] - prev_close).abs(),
            ),
        )
        self.ptf["atr_14"] = self.ptf["tr"].rolling(14).mean()
        self.ptf["vol_sma_20"] = self.ptf["volume"].rolling(20).mean()
        self.ptf["recent_high_20"] = self.ptf["high"].rolling(20).max().shift(1)

    def generate_signal(self, symbol: str, bar_index: int = -1) -> SignalResult:
        if bar_index < 0:
            bar_index = len(self.ptf) + bar_index

        if bar_index < 60 or len(self.htf) < 210:
            return SignalResult(symbol, "long", 0, 0, 0.0, "Insufficient data", False)

        # Use only data up to this bar — no future leak
        ptf = self.ptf.iloc[: bar_index + 1]
        # HTF aligned to current primary timestamp when possible
        current_time = ptf.index[-1]
        htf = self.htf[self.htf.index <= current_time]
        if len(htf) < 210:
            htf = self.htf.iloc[: max(210, min(len(self.htf), bar_index // 4 + 50))]

        regime = self.regime.evaluate(htf)

        close = float(ptf["close"].iloc[-1])
        sma20 = ptf["sma_20"].iloc[-1]
        roc = ptf["roc_10"].iloc[-1]
        recent_high = ptf["recent_high_20"].iloc[-1]
        vol = ptf["volume"].iloc[-1]
        vol_sma = ptf["vol_sma_20"].iloc[-1]
        atr = ptf["atr_14"].iloc[-1]

        if any(pd.isna(x) for x in [sma20, roc, recent_high, vol_sma, atr]):
            return SignalResult(symbol, "long", 0, 0, 0.0, "Indicators not ready", False)

        trend_score = 90.0 if regime.label == "bull" else 25.0
        structure_ok = close > float(recent_high)
        structure_score = 88.0 if structure_ok else 20.0
        momentum_ok = float(roc) > 0 and close > float(sma20)
        momentum_score = 85.0 if momentum_ok else 20.0

        atr_pct = float(atr) / close if close > 0 else 0
        vol_ok = float(vol) > float(vol_sma) * 1.15
        vol_in_band = 0.004 <= atr_pct <= 0.06

        volatility_score = 80.0 if vol_in_band else 15.0
        volume_score = 80.0 if vol_ok else 20.0
        liquidity_score = 75.0  # majors only universe already filtered
        regime_score = regime.score

        # Market structure as separate component
        components = {
            "trend": trend_score,
            "market_structure": structure_score,
            "momentum": momentum_score,
            "volatility": volatility_score,
            "volume": volume_score,
            "liquidity": liquidity_score,
            "regime": regime_score,
        }
        score = combine_scores(components)
        decision = gate(score)

        hard_fail = (
            regime.label != "bull"
            or not structure_ok
            or not momentum_ok
            or not vol_ok
            or not vol_in_band
        )
        if hard_fail:
            return SignalResult(
                symbol, "long", 0, 0, score,
                f"Hard filter fail | regime={regime.label} | {decision}",
                False, decision,
            )

        if decision in ("NO_TRADE", "WATCH"):
            return SignalResult(
                symbol, "long", 0, 0, score,
                f"Score gate {decision}", False, decision,
            )

        entry = close
        stop = entry - (float(atr) * 1.5)
        return SignalResult(
            symbol=symbol,
            side="long",
            entry_price=entry,
            stop_price=stop,
            score=score,
            reason=f"Passed | {decision} | {regime.reason}",
            is_valid=True,
            gate=decision,
        )
