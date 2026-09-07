"""
FATE QUANT — Risk Engine
Highest authority in the system (after Kill Switch).
"""

from config.settings import (
    RISK_PER_TRADE_PCT,
    MAX_DAILY_LOSS_PCT,
    MAX_DRAWDOWN_PCT,
    ALLOW_LIVE_TRADING,
)


class RiskEngine:
    def __init__(self, equity: float):
        self.equity = equity
        self.daily_pnl = 0.0
        self.peak_equity = equity
        self.is_locked = False
        self.lock_reason = None

    def update_equity(self, new_equity: float):
        self.equity = new_equity
        if new_equity > self.peak_equity:
            self.peak_equity = new_equity

    def check_kill_switch(self) -> bool:
        """
        Returns True if system must be locked.
        """
        # Daily loss check
        daily_loss_pct = -self.daily_pnl / self.equity if self.equity > 0 else 0
        if daily_loss_pct >= MAX_DAILY_LOSS_PCT:
            self._activate_kill_switch("Daily loss limit reached")
            return True

        # Drawdown check
        drawdown = (self.peak_equity - self.equity) / self.peak_equity if self.peak_equity > 0 else 0
        if drawdown >= MAX_DRAWDOWN_PCT:
            self._activate_kill_switch("Max drawdown reached")
            return True

        return False

    def _activate_kill_switch(self, reason: str):
        self.is_locked = True
        self.lock_reason = reason
        # In full implementation: cancel orders, stop new trades, alert owner

    def calculate_position_size(self, entry_price: float, stop_price: float) -> float:
        """
        Calculate position size so that loss at stop = exactly RISK_PER_TRADE_PCT of equity.
        Returns quantity in base asset. Returns 0 if risk cannot be respected.
        """
        if self.is_locked or not ALLOW_LIVE_TRADING:
            return 0.0

        if entry_price <= 0 or stop_price <= 0:
            return 0.0

        risk_amount = self.equity * RISK_PER_TRADE_PCT
        stop_distance = abs(entry_price - stop_price)

        if stop_distance == 0:
            return 0.0

        quantity = risk_amount / stop_distance

        # Final safety: never allow more risk than budgeted
        potential_loss = quantity * stop_distance
        if potential_loss > risk_amount * 1.01:  # 1% tolerance for rounding
            return 0.0

        return quantity

    def can_open_trade(self) -> bool:
        if self.is_locked:
            return False
        if self.check_kill_switch():
            return False
        return True
