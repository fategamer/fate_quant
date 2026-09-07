"""
FATE QUANT — Research Engine (Backtester)

Answers the question:
"If I had run these exact rules historically, what would have happened after realistic costs?"

Produces the full performance report required by the constitution.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
from config.settings import (
    TOTAL_CAPITAL_KES,
    RISK_PER_TRADE_PCT,
    TAKER_FEE,
    SLIPPAGE_PCT,
    MAX_DRAWDOWN_PCT,
)


@dataclass
class Trade:
    symbol: str
    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    entry_price: float
    exit_price: float
    quantity: float
    pnl: float
    pnl_pct: float
    fees: float
    side: str = "long"


@dataclass
class PerformanceReport:
    total_return_pct: float = 0.0
    max_drawdown_pct: float = 0.0
    win_rate: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    profit_factor: float = 0.0
    expectancy: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    total_trades: int = 0
    longest_losing_streak: int = 0
    total_fees: float = 0.0
    total_slippage_cost: float = 0.0
    final_equity: float = 0.0
    equity_curve: List[float] = field(default_factory=list)
    trades: List[Trade] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            "=" * 60,
            "FATE QUANT — RESEARCH ENGINE REPORT",
            "=" * 60,
            f"Total Return          : {self.total_return_pct:.2f}%",
            f"Max Drawdown          : {self.max_drawdown_pct:.2f}%",
            f"Win Rate              : {self.win_rate:.2f}%",
            f"Average Win           : {self.avg_win:.2f}",
            f"Average Loss          : {self.avg_loss:.2f}",
            f"Profit Factor         : {self.profit_factor:.2f}",
            f"Expectancy            : {self.expectancy:.4f}",
            f"Sharpe Ratio          : {self.sharpe_ratio:.2f}",
            f"Sortino Ratio         : {self.sortino_ratio:.2f}",
            f"Total Trades          : {self.total_trades}",
            f"Longest Losing Streak : {self.longest_losing_streak}",
            f"Total Fees            : {self.total_fees:.2f}",
            f"Slippage Cost         : {self.total_slippage_cost:.2f}",
            f"Final Equity          : {self.final_equity:.2f}",
            "=" * 60,
        ]
        return "\n".join(lines)


class ResearchEngine:
    def __init__(self, initial_capital: float = TOTAL_CAPITAL_KES):
        self.initial_capital = initial_capital
        self.equity = initial_capital
        self.peak_equity = initial_capital
        self.trades: List[Trade] = []
        self.equity_curve: List[float] = [initial_capital]

    def apply_costs(self, price: float, quantity: float, is_entry: bool) -> float:
        """Apply fee + slippage. Returns cost in quote currency."""
        notional = price * quantity
        fee = notional * TAKER_FEE
        slippage = notional * SLIPPAGE_PCT
        return fee + slippage

    def run_simple_backtest(
        self,
        signals: List[dict],
        price_data: Dict[str, pd.DataFrame],
    ) -> PerformanceReport:
        """
        Very early research engine.
        signals: list of dicts with symbol, entry_time, entry_price, stop_price, score
        This is a placeholder that will be expanded into full bar-by-bar simulation.
        """
        # Placeholder structure — full engine comes next
        report = PerformanceReport()
        report.final_equity = self.equity
        report.equity_curve = self.equity_curve
        return report

    def calculate_metrics(self, trades: List[Trade]) -> PerformanceReport:
        if not trades:
            return PerformanceReport(final_equity=self.initial_capital)

        pnls = [t.pnl for t in trades]
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p <= 0]

        total_return = (self.equity - self.initial_capital) / self.initial_capital * 100

        # Max drawdown from equity curve
        equity_arr = np.array(self.equity_curve)
        peak = np.maximum.accumulate(equity_arr)
        dd = (peak - equity_arr) / peak
        max_dd = dd.max() * 100 if len(dd) > 0 else 0.0

        win_rate = len(wins) / len(trades) * 100 if trades else 0.0
        avg_win = np.mean(wins) if wins else 0.0
        avg_loss = np.mean(losses) if losses else 0.0

        gross_profit = sum(wins)
        gross_loss = abs(sum(losses))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0.0

        expectancy = np.mean(pnls) if pnls else 0.0

        # Simple Sharpe / Sortino (daily returns approximation later)
        returns = pd.Series(pnls)
        sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0.0
        downside = returns[returns < 0]
        sortino = (returns.mean() / downside.std()) * np.sqrt(252) if len(downside) > 0 and downside.std() > 0 else 0.0

        # Longest losing streak
        streak = 0
        max_streak = 0
        for p in pnls:
            if p <= 0:
                streak += 1
                max_streak = max(max_streak, streak)
            else:
                streak = 0

        total_fees = sum(t.fees for t in trades)

        return PerformanceReport(
            total_return_pct=total_return,
            max_drawdown_pct=max_dd,
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            expectancy=expectancy,
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            total_trades=len(trades),
            longest_losing_streak=max_streak,
            total_fees=total_fees,
            final_equity=self.equity,
            equity_curve=self.equity_curve,
            trades=trades,
        )
