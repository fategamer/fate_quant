"""
FATE QUANT — Data Handler
Responsible only for fetching and validating market data.
No strategy logic lives here.
"""

from typing import Optional
import pandas as pd
from config.settings import ALLOWED_SYMBOLS, PRIMARY_TIMEFRAME, HIGHER_TIMEFRAME


class DataHandler:
    def __init__(self, exchange_id: str = "binance"):
        self.exchange_id = exchange_id
        self._exchange = None

    def _get_exchange(self):
        if self._exchange is None:
            import ccxt
            self._exchange = getattr(ccxt, self.exchange_id)({
                "enableRateLimit": True,
                "options": {"defaultType": "spot"},
            })
        return self._exchange

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 500,
        since: Optional[int] = None,
    ) -> pd.DataFrame:
        if symbol not in ALLOWED_SYMBOLS:
            raise ValueError(f"{symbol} not in allowed universe")

        exchange = self._get_exchange()
        raw = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit, since=since)

        df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        return df

    def validate_data(self, df: pd.DataFrame) -> bool:
        """Basic data integrity checks."""
        if df is None or df.empty:
            return False
        if df.isnull().any().any():
            return False
        if (df[["open", "high", "low", "close"]] <= 0).any().any():
            return False
        if (df["high"] < df["low"]).any():
            return False
        return True
