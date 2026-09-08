"""
FATE QUANT — Phase E Paper Trading
Real market data. Real decisions. Zero real money.
"""

import sys
import os
import time
import argparse
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import TOTAL_CAPITAL_KES, INITIAL_LIVE_ALLOCATION_PCT, ALLOW_LIVE_TRADING


def main():
    parser = argparse.ArgumentParser(description="FATE QUANT paper trader")
    parser.add_argument("--loops", type=int, default=1)
    parser.add_argument("--sleep", type=int, default=60)
    args = parser.parse_args()

    print("=" * 60)
    print("FATE QUANT V1 — PHASE E PAPER TRADING")
    print("=" * 60)
    print(f"Total capital         : KES {TOTAL_CAPITAL_KES:,}")
    print(f"Paper allocation (10%): KES {TOTAL_CAPITAL_KES * INITIAL_LIVE_ALLOCATION_PCT:,.0f}")
    print(f"Live trading flag     : {ALLOW_LIVE_TRADING}")
    print("Orders sent to exchange: NEVER")
    print("=" * 60)

    if ALLOW_LIVE_TRADING:
        print("REFUSING TO START: live trading flag is True.")
        return

    try:
        from execution.paper_engine import PaperEngine
        engine = PaperEngine()
    except ModuleNotFoundError as e:
        print("Missing package:", e)
        print("Fix: pip install -r requirements.txt")
        return
    except Exception as e:
        print("Could not start paper engine:")
        print(e)
        traceback.print_exc()
        return

    for i in range(args.loops):
        print(f"\n--- Cycle {i + 1}/{args.loops} ---")
        try:
            status = engine.run_once()
        except Exception as e:
            print("Scan failed:")
            print(e)
            traceback.print_exc()
            return
        print(
            f"Equity={status['equity']:.2f} Cash={status['cash']:.2f} "
            f"Open={status['open']} Closed={status['closed']} "
            f"Locked={status['locked']}"
        )
        if status["locked"]:
            print(f"SYSTEM LOCKED: {status['lock_reason']}")
            break
        if i < args.loops - 1:
            time.sleep(args.sleep)

    print("\nPaper session finished. No live orders were sent.")


if __name__ == "__main__":
    main()
