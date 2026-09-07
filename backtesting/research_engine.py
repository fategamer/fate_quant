"""
FATE QUANT — Research Engine (Backtester)

Answers:
"If I had run these exact rules historically, what would have happened after realistic costs?"

Full bar-by-bar simulation with fees, slippage, position sizing, and kill-switch respect.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import pandas as pd
import numpy as np
from config.settings import (
    TOTAL_CAPITAL_KES,
    RISK_PER_TRADE_PCT,
    TAKER_FEE,
    SLIPPAGE_PCT,
    MAX_DRAWDOWN_PCT,
    MAX_DAILY_LOSS_PCT,
    KILL_SWITCH,
)
from risk.risk_engine import RiskEngine, PositionSizeResult
from strategies.trend_momentum_breakout import TrendMomentumBreakout, SignalResult


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
    exit_reason: str = ""


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
    notes: str = ""

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
        if self.notes:
            lines.append(f"Notes: {self.notes}")
        return "\n".join(lines)


class ResearchEngine:
    def __init__(self, initial_capital: float = TOTAL_CAPITAL_KES):
        self.initial_capital = initial_capital
        self.equity = initial_capital
        self.peak_equity = initial_capital
        self.trades: List[Trade] = []
        self.equity_curve: List[float] = [initial_capital]
        # Research mode = True so position sizing is allowed for simulation
        self.risk = RiskEngine(equity=initial_capital, research_mode=True)

    def _apply_entry_costs(self, price: float, quantity: float) -> Tuple[float, float]:
        """Returns (effective_entry_price, total_cost)"""
        slippage = price * SLIPPAGE_PCT
        effective_price = price + slippage          # buy higher
        fee = effective_price * quantity * TAKER_FEE
        return effective_price, fee

    def _apply_exit_costs(self, price: float, quantity: float) -> Tuple[float, float]:
        """Returns (effective_exit_price, total_cost)"""
        slippage = price * SLIPPAGE_PCT
        effective_price = price - slippage          # sell lower
        fee = effective_price * quantity * TAKER_FEE
        return effective_price, fee

    def run_bar_by_bar(
        self,
        symbol: str,
        htf_df: pd.DataFrame,
        ptf_df: pd.DataFrame,
        max_bars: Optional[int] = None,
    ) -> PerformanceReport:
        """
        Full bar-by-bar simulation for one symbol.
        Uses higher timeframe for regime/trend and primary timeframe for entries/exits.
        """
        if htf_df.empty or ptf_df.empty:
            return PerformanceReport(notes="Empty data")

        strategy = TrendMomentumBreakout(htf_df, ptf_df)

        df = ptf_df.copy()
        if max_bars:
            df = df.iloc[-max_bars:]

        position_open = False
        entry_price = 0.0
        stop_price = 0.0
        quantity = 0.0
        entry_time = None
        entry_fees = 0.0

        for i in range(50, len(df)):
            current_bar = df.iloc[i]
            current_time = df.index[i]
            high = current_bar["high"]
            low = current_bar["low"]
            close = current_bar["close"]

            self.risk.update_equity(self.equity)

            if self.risk.check_kill_switch():
                if position_open:
                    eff_exit, exit_fee = self._apply_exit_costs(close, quantity)
                    pnl = (eff_exit - entry_price) * quantity - entry_fees - exit_fee
                    self.equity += pnl
                    self.trades.append(Trade(
                        symbol=symbol,
                        entry_time=entry_time,
                        exit_time=current_time,
                        entry_price=entry_price,
                        exit_price=eff_exit,
                        quantity=quantity,
                        pnl=pnl,
                        pnl_pct=(pnl / (entry_price * quantity)) * 100 if entry_price * quantity > 0 else 0,
                        fees=entry_fees + exit_fee,
                        exit_reason="Kill Switch",
                    ))
                    position_open = False
                break

            if position_open:
                # Stop loss
                if low <= stop_price:
                    eff_exit, exit_fee = self._apply_exit_costs(stop_price, quantity)
                    pnl = (eff_exit - entry_price) * quantity - entry_fees - exit_fee
                    self.equity += pnl
                    self.risk.update_equity(self.equity, trade_pnl=pnl)

                    self.trades.append(Trade(
                        symbol=symbol,
                        entry_time=entry_time,
                        exit_time=current_time,
                        entry_price=entry_price,
                        exit_price=eff_exit,
                        quantity=quantity,
                        pnl=pnl,
                        pnl_pct=(pnl / (entry_price * quantity)) * 100 if entry_price * quantity > 0 else 0,
                        fees=entry_fees + exit_fee,
                        exit_reason="Stop Loss",
                    ))
                    position_open = False
                    self.equity_curve.append(self.equity)
                    continue

                # Take profit 2R
                risk_dist = entry_price - stop_price
                take_profit = entry_price + (risk_dist * 2.0)
                if high >= take_profit:
                    eff_exit, exit_fee = self._apply_exit_costs(take_profit, quantity)
                    pnl = (eff_exit - entry_price) * quantity - entry_fees - exit_fee
                    self.equity += pnl
                    self.risk.update_equity(self.equity, trade_pnl=pnl)

                    self.trades.append(Trade(
                        symbol=symbol,
                        entry_time=entry_time,
                        exit_time=current_time,
                        entry_price=entry_price,
                        exit_price=eff_exit,
                        quantity=quantity,
                        pnl=pnl,
                        pnl_pct=(pnl / (entry_price * quantity)) * 100 if entry_price * quantity > 0 else 0,
                        fees=entry_fees + exit_fee,
                        exit_reason="Take Profit 2R",
                    ))
                    position_open = False
                    self.equity_curve.append(self.equity)
                    continue

            else:
                signal = strategy.generate_signal(symbol)

                if signal.is_valid and signal.score >= 80:
                    size_result: PositionSizeResult = self.risk.calculate_position_size(
                        entry_price=signal.entry_price,
                        stop_price=signal.stop_price,
                    )

                    if not size_result.rejected and size_result.quantity > 0:
                        eff_entry, entry_fee = self._apply_entry_costs(signal.entry_price, size_result.quantity)
                        entry_price = eff_entry
                        stop_price = signal.stop_price
                        quantity = size_result.quantity
                        entry_time = current_time
                        entry_fees = entry_fee
                        position_open = True
                        self.equity -= entry_fee

            self.equity_curve.append(self.equity)

        # Close remaining position at end
        if position_open:
            last_close = df["close"].iloc[-1]
            last_time = df.index[-1]
            eff_exit, exit_fee = self._apply_exit_costs(last_close, quantity)
            pnl = (eff_exit - entry_price) * quantity - entry_fees - exit_fee
            self.equity += pnl
            self.trades.append(Trade(
                symbol=symbol,
                entry_time=entry_time,
                exit_time=last_time,
                entry_price=entry_price,
                exit_price=eff_exit,
                quantity=quantity,
                pnl=pnl,
                pnl_pct=(pnl / (entry_price * quantity)) * 100 if entry_price * quantity > 0 else 0,
                fees=entry_fees + exit_fee,
                exit_reason="End of data",
            ))
            self.equity_curve.append(self.equity)

        return self.calculate_metrics(self.trades)

    def calculate_metrics(self, trades: List[Trade]) -> PerformanceReport:
        if not trades:
            return PerformanceReport(
                final_equity=self.initial_capital,
                equity_curve=self.equity_curve,
                notes="No trades generated",
            )

        pnls = [t.pnl for t in trades]
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p <= 0]

        total_return = (self.equity - self.initial_capital) / self.initial_capital * 100

        equity_arr = np.array(self.equity_curve)
        peak = np.maximum.accumulate(equity_arr)
        dd = (peak - equity_arr) / np.where(peak == 0, 1, peak)
        max_dd = float(dd.max() * 100) if len(dd) > 0 else 0.0

        win_rate = len(wins) / len(trades) * 100 if trades else 0.0
        avg_win = float(np.mean(wins)) if wins else 0.0
        avg_loss = float(np.mean(losses)) if losses else 0.0

        gross_profit = sum(wins)
        gross_loss = abs(sum(losses))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0.0

        expectancy = float(np.mean(pnls)) if pnls else 0.0

        returns = pd.Series(pnls)
        sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0.0
        downside = returns[returns < 0]
        sortino = (returns.mean() / downside.std()) * np.sqrt(252) if len(downside) > 0 and downside.std() > 0 else 0.0

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
            sharpe_ratio=float(sharpe),
            sortino_ratio=float(sortino),
            total_trades=len(trades),
            longest_losing_streak=max_streak,
            total_fees=total_fees,
            final_equity=self.equity,
            equity_curve=self.equity_curve,
            trades=trades,
        )
