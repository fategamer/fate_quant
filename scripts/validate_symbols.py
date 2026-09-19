from config.settings import ALLOWED_SYMBOLS, MONITOR_SYMBOLS
from data.data_handler import DataHandler


def main():
    symbols = [*ALLOWED_SYMBOLS, *MONITOR_SYMBOLS]
    results = DataHandler().validate_symbols(symbols)

    print("FATE QUANT — Binance SPOT symbol validation")
    core_available = True
    for symbol in symbols:
        info = results[symbol]
        status = "AVAILABLE" if info["available"] else "UNAVAILABLE"
        print(
            f"{symbol}: {status} "
            f"status={info['status']} "
            f"spot_trading_allowed={info['spot_trading_allowed']}"
        )
        if symbol in ALLOWED_SYMBOLS:
            core_available = core_available and info["available"]

    if not core_available:
        raise SystemExit("One or more core symbols are unavailable on Binance SPOT.")


if __name__ == "__main__":
    main()
