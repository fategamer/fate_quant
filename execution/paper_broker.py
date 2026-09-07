"""
FATE QUANT — Paper Broker
Simulates fills. Never sends real exchange orders.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timezone
from config.settings import TAKER_FEE, SLIPPAGE_PCT


@dataclass
class PaperFill:
    symbol: str
    side: str
    quantity: float
    requested_price: float
    fill_price: float
    fee: float
    timestamp: datetime
    reason: str


class PaperBroker:
    """
    Conservative fill model:
    - Buys fill slightly worse (price + slippage)
    - Sells fill slightly worse (price - slippage)
    - Fee applied on fill notional
    """

    def buy(self, symbol: str, quantity: float, price: float, reason: str = "") -> PaperFill:
        fill_price = price * (1 + SLIPPAGE_PCT)
        fee = fill_price * quantity * TAKER_FEE
        return PaperFill(
            symbol=symbol,
            side="buy",
            quantity=quantity,
            requested_price=price,
            fill_price=fill_price,
            fee=fee,
            timestamp=datetime.now(timezone.utc),
            reason=reason,
        )

    def sell(self, symbol: str, quantity: float, price: float, reason: str = "") -> PaperFill:
        fill_price = price * (1 - SLIPPAGE_PCT)
        fee = fill_price * quantity * TAKER_FEE
        return PaperFill(
            symbol=symbol,
            side="sell",
            quantity=quantity,
            requested_price=price,
            fill_price=fill_price,
            fee=fee,
            timestamp=datetime.now(timezone.utc),
            reason=reason,
        )
