from config.settings import ALLOWED_SYMBOLS, MONITOR_SYMBOLS
from data.data_handler import DataHandler


def main():
    symbols = [*ALLOWED_SYMBOLS, *MONITOR_SYMBOLS]
    results = DataHandler().validate_symbols(symbols)

    print("FATE QUANT — Binance SPOT symbol validation")
    all_available = True
    for symbol in symbols:
        info = results[symbol]
        status = "AVAILABLE" if info["available"] else "UNAVAILABLE"
        print(
            f"{symbol}: {status} "
            f"status={info['status']} "
            f"spot_trading_allowed={info['spot_trading_allowed']}"
        )
        all_available = all_available and info["available"]

    if not all_available:
        raise SystemExit("One or more configured symbols are unavailable on Binance SPOT.")


if __name__ == "__main__":
    main()
