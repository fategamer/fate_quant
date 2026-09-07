"""
FATE QUANT — Binance Spot Testnet Broker

Uses Binance Spot TESTNET only.
Never points at live/mainnet endpoints.
"""

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from config.settings import ALLOWED_SYMBOLS, MARKET_TYPE

TESTNET_REST = "https://testnet.binance.vision/api"


@dataclass
class TestnetFill:
    symbol: str
    side: str
    quantity: float
    price: float
    order_id: Optional[str]
    status: str
    timestamp: datetime
    raw: dict


class TestnetBroker:
    def __init__(self):
        self.api_key = os.getenv("BINANCE_TESTNET_API_KEY", "").strip()
        self.api_secret = os.getenv("BINANCE_TESTNET_API_SECRET", "").strip()
        self._exchange = None

    def ready(self) -> tuple[bool, str]:
        if MARKET_TYPE != "spot":
            return False, "Only spot is allowed"
        if not self.api_key or not self.api_secret:
            return False, "Missing BINANCE_TESTNET_API_KEY / BINANCE_TESTNET_API_SECRET"
        return True, "OK"

    def _client(self):
        if self._exchange is None:
            import ccxt
            ready, reason = self.ready()
            if not ready:
                raise RuntimeError(reason)
            self._exchange = ccxt.binance({
                "apiKey": self.api_key,
                "secret": self.api_secret,
                "enableRateLimit": True,
                "options": {"defaultType": "spot"},
            })
            # Force testnet URLs. Never mainnet.
            self._exchange.set_sandbox_mode(True)
            self._exchange.urls["api"]["public"] = TESTNET_REST
            self._exchange.urls["api"]["private"] = TESTNET_REST
        return self._exchange

    def fetch_balance_usdt(self) -> float:
        bal = self._client().fetch_balance()
        free = bal.get("free", {})
        return float(free.get("USDT", 0.0) or 0.0)

    def market_buy(self, symbol: str, quantity: float) -> TestnetFill:
        if symbol not in ALLOWED_SYMBOLS:
            raise ValueError(f"{symbol} not allowed")
        order = self._client().create_order(
            symbol=symbol,
            type="market",
            side="buy",
            amount=quantity,
        )
        return self._to_fill(symbol, "buy", quantity, order)

    def market_sell(self, symbol: str, quantity: float) -> TestnetFill:
        if symbol not in ALLOWED_SYMBOLS:
            raise ValueError(f"{symbol} not allowed")
        order = self._client().create_order(
            symbol=symbol,
            type="market",
            side="sell",
            amount=quantity,
        )
        return self._to_fill(symbol, "sell", quantity, order)

    def _to_fill(self, symbol: str, side: str, quantity: float, order: dict) -> TestnetFill:
        price = 0.0
        if order.get("average"):
            price = float(order["average"])
        elif order.get("price"):
            price = float(order["price"])
        return TestnetFill(
            symbol=symbol,
            side=side,
            quantity=float(order.get("filled") or quantity),
            price=price,
            order_id=str(order.get("id")) if order.get("id") is not None else None,
            status=str(order.get("status", "unknown")),
            timestamp=datetime.now(timezone.utc),
            raw=order,
        )
