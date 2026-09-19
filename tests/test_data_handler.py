import pandas as pd

from data.data_handler import DataHandler


def test_validate_symbols_reports_spot_availability(monkeypatch):
    payload = {
        "symbols": [
            {"symbol": "BTCUSDT", "status": "TRADING", "isSpotTradingAllowed": True},
            {"symbol": "FAKEUSDT", "status": "BREAK", "isSpotTradingAllowed": False},
        ]
    }

    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return payload

    monkeypatch.setattr("data.data_handler.requests.get", lambda *args, **kwargs: Response())

    result = DataHandler().validate_symbols(["BTC/USDT", "FAKE/USDT"])

    assert result["BTC/USDT"]["available"] is True
    assert result["BTC/USDT"]["status"] == "TRADING"
    assert result["FAKE/USDT"]["available"] is False
    assert result["FAKE/USDT"]["status"] == "BREAK"


def test_validate_symbols_marks_missing_pair_unavailable(monkeypatch):
    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return {"symbols": []}

    monkeypatch.setattr("data.data_handler.requests.get", lambda *args, **kwargs: Response())

    result = DataHandler().validate_symbols(["MISSING/USDT"])

    assert result["MISSING/USDT"]["available"] is False
    assert result["MISSING/USDT"]["status"] == "NOT_FOUND"


def test_monitored_symbol_can_fetch_ohlcv(monkeypatch):
    handler = DataHandler()

    raw = [[
        1704067200000, "100", "101", "99", "100.5", "1000",
        1704070799999, "100000", 100, "500", "50000", "0"
    ]]

    monkeypatch.setattr(handler, "_get_exchange", lambda: (_ for _ in ()).throw(RuntimeError("offline")))
    monkeypatch.setattr(handler, "_fetch_rest", lambda *args, **kwargs: handler._from_klines(raw))

    df = handler.fetch_ohlcv("XLM/USDT", "1h", limit=1)

    assert not df.empty
    assert df.iloc[0]["close"] == 100.5
