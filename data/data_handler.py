"""
FATE QUANT — Data Handler
Fetch + validate OHLCV. Tries ccxt, then public REST fallbacks.
"""

from typing import Optional
import pandas as pd
import requests
from config.settings import ALLOWED_SYMBOLS

INTERVAL_MAP = {
    "1m": "1m", "5m": "5m", "15m": "15m", "1h": "1h", "4h": "4h", "1d": "1d",
}

REST_BASES = [
    "https://data-api.binance.vision",
    "https://api.binance.com",
]


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

    def _symbol_to_pair(self, symbol: str) -> str:
        return symbol.replace("/", "")

    def _from_klines(self, raw) -> pd.DataFrame:
        df = pd.DataFrame(raw, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "qav", "trades", "tbb", "tbq", "ignore",
        ][: len(raw[0])])
        df = df.iloc[:, :6]
        df.columns = ["timestamp", "open", "high", "low", "close", "volume"]
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df.set_index("timestamp", inplace=True)
        return df

    def _fetch_rest(self, symbol: str, timeframe: str, limit: int) -> pd.DataFrame:
        pair = self._symbol_to_pair(symbol)
        interval = INTERVAL_MAP.get(timeframe, timeframe)
        last_error = None
        for base in REST_BASES:
            url = f"{base}/api/v3/klines"
            try:
                resp = requests.get(
                    url,
                    params={"symbol": pair, "interval": interval, "limit": limit},
                    timeout=20,
                )
                data = resp.json()
                if isinstance(data, dict) and data.get("msg"):
                    last_error = data.get("msg")
                    continue
                if not isinstance(data, list) or not data:
                    last_error = f"empty response from {base}"
                    continue
                return self._from_klines(data)
            except Exception as e:
                last_error = str(e)
                continue
        raise RuntimeError(f"Could not fetch {symbol} {timeframe}. Last error: {last_error}")

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 500,
        since: Optional[int] = None,
    ) -> pd.DataFrame:
        if symbol not in ALLOWED_SYMBOLS:
            raise ValueError(f"{symbol} not in allowed universe")

        try:
            exchange = self._get_exchange()
            raw = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit, since=since)
            df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)
            if self.validate_data(df):
                return df
        except Exception:
            pass

        return self._fetch_rest(symbol, timeframe, limit)

    def validate_data(self, df: pd.DataFrame) -> bool:
        if df is None or df.empty:
            return False
        if df.isnull().any().any():
            return False
        if (df[["open", "high", "low", "close"]] <= 0).any().any():
            return False
        if (df["high"] < df["low"]).any():
            return False
        return True
