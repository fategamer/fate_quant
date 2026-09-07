"""
FATE QUANT — Phase F Testnet runner

Requires .env with BINANCE_TESTNET_API_KEY and BINANCE_TESTNET_API_SECRET.
Does not use mainnet. Does not use real KES 10,000.
"""

import sys
import os
import time
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from config.settings import ALLOW_LIVE_TRADING, ALLOWED_SYMBOLS, TOTAL_CAPITAL_KES
from execution.testnet_engine import TestnetEngine


def main():
    parser = argparse.ArgumentParser(description="FATE QUANT Binance Spot Testnet")
    parser.add_argument("--loops", type=int, default=1)
    parser.add_argument("--sleep", type=int, default=60)
    args = parser.parse_args()

    print("=" * 60)
    print("FATE QUANT V1 — PHASE F TESTNET")
    print("=" * 60)
    print(f"Universe              : {ALLOWED_SYMBOLS}")
    print(f"Reference capital     : KES {TOTAL_CAPITAL_KES:,}")
    print(f"Live trading flag     : {ALLOW_LIVE_TRADING}")
    print("Target                : Binance Spot TESTNET only")
    print("Real funds            : NOT USED")
    print("=" * 60)

    if ALLOW_LIVE_TRADING:
        print("REFUSING TO START: live trading is enabled.")
        return

    try:
        engine = TestnetEngine()
    except Exception as e:
        print(f"Cannot start testnet engine: {e}")
        print("Create a .env from config/secrets.example.env and add TESTNET keys only.")
        return

    for i in range(args.loops):
        print(f"\n--- Cycle {i + 1}/{args.loops} ---")
        status = engine.run_once()
        print(
            f"Equity={status['equity']:.2f} Cash={status['cash']:.2f} "
            f"Open={status['open']} Closed={status['closed']} Locked={status['locked']}"
        )
        if status["locked"]:
            print(f"SYSTEM LOCKED: {status['lock_reason']}")
            break
        if i < args.loops - 1:
            time.sleep(args.sleep)

    print("\nTestnet session finished.")


if __name__ == "__main__":
    main()
