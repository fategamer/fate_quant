"""
FATE QUANT — Risk Engine
Highest authority after Kill Switch.
Clean separation: this module only decides whether risk is acceptable
and calculates position size. It never generates signals.
"""

from dataclasses import dataclass
from typing import Optional
from config.settings import (
    RISK_PER_TRADE_PCT,
    MAX_DAILY_LOSS_PCT,
    MAX_DRAWDOWN_PCT,
    KILL_SWITCH,
    ALLOW_LIVE_TRADING,
)


@dataclass
class PositionSizeResult:
    quantity: float
    risk_amount: float
    rejected: bool
    reason: Optional[str] = None


class RiskEngine:
    def __init__(self, equity: float):
        self.equity = equity
        self.peak_equity = equity
        self.daily_pnl = 0.0
        self.consecutive_losses = 0
        self.is_locked = False
        self.lock_reason: Optional[str] = None

    def update_equity(self, new_equity: float, trade_pnl: float = 0.0):
        self.equity = new_equity
        self.daily_pnl += trade_pnl

        if new_equity > self.peak_equity:
            self.peak_equity = new_equity

        if trade_pnl < 0:
            self.consecutive_losses += 1
        elif trade_pnl > 0:
            self.consecutive_losses = 0

    def reset_daily(self):
        self.daily_pnl = 0.0

    def check_kill_switch(self) -> bool:
        """Returns True if system must lock."""
        if self.is_locked:
            return True

        # Daily loss
        if self.equity > 0:
            daily_loss_pct = -self.daily_pnl / self.equity
            if daily_loss_pct >= KILL_SWITCH["daily_loss_pct"]:
                self._activate("Daily loss limit reached")
                return True

        # Max drawdown from peak
        if self.peak_equity > 0:
            drawdown = (self.peak_equity - self.equity) / self.peak_equity
            if drawdown >= KILL_SWITCH["max_drawdown_pct"]:
                self._activate("Max drawdown reached")
                return True

        # Consecutive losses
        if self.consecutive_losses >= KILL_SWITCH["max_consecutive_losses"]:
            self._activate(f"{self.consecutive_losses} consecutive losses")
            return True

        return False

    def _activate(self, reason: str):
        self.is_locked = True
        self.lock_reason = reason

    def can_open_trade(self) -> tuple[bool, str]:
        if not ALLOW_LIVE_TRADING:
            return False, "Live trading disabled by constitution"
        if self.is_locked:
            return False, f"System locked: {self.lock_reason}"
        if self.check_kill_switch():
            return False, f"Kill switch: {self.lock_reason}"
        return True, "OK"

    def calculate_position_size(
        self,
        entry_price: float,
        stop_price: float,
    ) -> PositionSizeResult:
        """
        Position Size = (Equity × Risk%) / Stop Distance

        If the calculated risk would exceed the budget → REJECT.
        """
        can_trade, reason = self.can_open_trade()
        if not can_trade:
            return PositionSizeResult(0.0, 0.0, True, reason)

        if entry_price <= 0 or stop_price <= 0:
            return PositionSizeResult(0.0, 0.0, True, "Invalid prices")

        risk_amount = self.equity * RISK_PER_TRADE_PCT
        stop_distance = abs(entry_price - stop_price)

        if stop_distance == 0:
            return PositionSizeResult(0.0, 0.0, True, "Zero stop distance")

        quantity = risk_amount / stop_distance

        # Final safety check
        potential_loss = quantity * stop_distance
        if potential_loss > risk_amount * 1.01:
            return PositionSizeResult(0.0, 0.0, True, "Risk budget exceeded")

        return PositionSizeResult(
            quantity=quantity,
            risk_amount=risk_amount,
            rejected=False,
            reason=None,
        )
