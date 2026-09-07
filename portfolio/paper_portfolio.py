"""
FATE QUANT — Paper Portfolio
Tracks cash, open positions, and equity. No exchange account.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, List
from datetime import datetime, timezone


@dataclass
class OpenPosition:
    symbol: str
    quantity: float
    entry_price: float
    stop_price: float
    take_profit: float
    entry_time: datetime
    entry_fee: float


@dataclass
class ClosedTrade:
    symbol: str
    entry_price: float
    exit_price: float
    quantity: float
    pnl: float
    fees: float
    entry_time: datetime
    exit_time: datetime
    reason: str


class PaperPortfolio:
    def __init__(self, starting_cash: float):
        self.starting_cash = starting_cash
        self.cash = starting_cash
        self.positions: Dict[str, OpenPosition] = {}
        self.closed: List[ClosedTrade] = []
        self.peak_equity = starting_cash

    def has_position(self, symbol: str) -> bool:
        return symbol in self.positions

    def open_count(self) -> int:
        return len(self.positions)

    def mark_to_market(self, last_prices: Dict[str, float]) -> float:
        value = self.cash
        for symbol, pos in self.positions.items():
            price = last_prices.get(symbol, pos.entry_price)
            value += pos.quantity * price
        if value > self.peak_equity:
            self.peak_equity = value
        return value

    def open_long(
        self,
        symbol: str,
        quantity: float,
        fill_price: float,
        stop_price: float,
        take_profit: float,
        fee: float,
    ) -> bool:
        cost = fill_price * quantity + fee
        if cost > self.cash:
            return False
        if symbol in self.positions:
            return False

        self.cash -= cost
        self.positions[symbol] = OpenPosition(
            symbol=symbol,
            quantity=quantity,
            entry_price=fill_price,
            stop_price=stop_price,
            take_profit=take_profit,
            entry_time=datetime.now(timezone.utc),
            entry_fee=fee,
        )
        return True

    def close_long(
        self,
        symbol: str,
        fill_price: float,
        fee: float,
        reason: str,
    ) -> Optional[ClosedTrade]:
        pos = self.positions.get(symbol)
        if not pos:
            return None

        proceeds = fill_price * pos.quantity - fee
        self.cash += proceeds
        pnl = (fill_price - pos.entry_price) * pos.quantity - pos.entry_fee - fee

        trade = ClosedTrade(
            symbol=symbol,
            entry_price=pos.entry_price,
            exit_price=fill_price,
            quantity=pos.quantity,
            pnl=pnl,
            fees=pos.entry_fee + fee,
            entry_time=pos.entry_time,
            exit_time=datetime.now(timezone.utc),
            reason=reason,
        )
        self.closed.append(trade)
        del self.positions[symbol]
        return trade
