"""
Show which integrations are configured.
Never prints tokens or API keys.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from config.settings import ALLOW_LIVE_TRADING, ALLOWED_SYMBOLS


def masked(name: str) -> str:
    value = os.getenv(name, "").strip()
    return "SET" if value else "MISSING"


def main():
    print("FATE QUANT — integration check")
    print(f"Symbols              : {ALLOWED_SYMBOLS}")
    print(f"Live trading         : {ALLOW_LIVE_TRADING}")
    print(f"Telegram token       : {masked('TELEGRAM_BOT_TOKEN')}")
    print(f"Telegram chat id     : {masked('TELEGRAM_CHAT_ID')}")
    print(f"Binance testnet key  : {masked('BINANCE_TESTNET_API_KEY')}")
    print(f"Binance testnet secret: {masked('BINANCE_TESTNET_API_SECRET')}")
    print()
    if ALLOW_LIVE_TRADING:
        print("WARNING: live trading flag is on. Engines should refuse.")
    else:
        print("Live trading is locked. Good.")
    print()
    print("Next:")
    print("  python scripts/setup_binance_testnet.py")
    print("  python scripts/run_paper.py")
    print("  python scripts/run_testnet.py")


if __name__ == "__main__":
    main()
