"""
FATE QUANT V1.0 — Entry Point
Default state: NO TRADE
"""

from config.settings import (
    TOTAL_CAPITAL_KES,
    ALLOW_LIVE_TRADING,
    ALLOWED_SYMBOLS,
)
from risk.risk_engine import RiskEngine


def main():
    print("=" * 60)
    print("FATE QUANT V1.0")
    print("Mission: Protect capital first. Trade only with measurable edge.")
    print("=" * 60)
    print(f"Total Capital          : KES {TOTAL_CAPITAL_KES:,}")
    print(f"Live Trading Allowed   : {ALLOW_LIVE_TRADING}")
    print(f"Allowed Symbols        : {ALLOWED_SYMBOLS}")
    print("Default state          : NO TRADE")
    print("=" * 60)

    # Initialize risk engine with total capital (live allocation handled later)
    risk = RiskEngine(equity=TOTAL_CAPITAL_KES)

    if risk.is_locked:
        print(f"SYSTEM LOCKED: {risk.lock_reason}")
        return

    print("Risk Engine initialized. Awaiting valid signals...")
    # Future: start data feed → regime → signals → risk check → execution


if __name__ == "__main__":
    main()
