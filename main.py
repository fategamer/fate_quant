"""
FATE QUANT V1.0 — Entry Point
Default state: NO TRADE
"""

from config.settings import (
    TOTAL_CAPITAL_KES,
    ALLOW_LIVE_TRADING,
    ALLOWED_SYMBOLS,
    RISK_PER_TRADE_PCT,
    MAX_DAILY_LOSS_PCT,
    MAX_DRAWDOWN_PCT,
)
from risk.risk_engine import RiskEngine


def main():
    print("=" * 60)
    print("FATE QUANT V1.0 — Research Mode")
    print("Mission: Protect capital first. Trade only with measurable edge.")
    print("=" * 60)
    print(f"Total Capital          : KES {TOTAL_CAPITAL_KES:,}")
    print(f"Risk per trade         : {RISK_PER_TRADE_PCT*100:.2f}%")
    print(f"Max Daily Loss         : {MAX_DAILY_LOSS_PCT*100:.1f}%")
    print(f"Max Drawdown           : {MAX_DRAWDOWN_PCT*100:.1f}%")
    print(f"Live Trading Allowed   : {ALLOW_LIVE_TRADING}")
    print(f"Allowed Symbols        : {ALLOWED_SYMBOLS}")
    print("Default state          : NO TRADE")
    print("=" * 60)

    risk = RiskEngine(equity=TOTAL_CAPITAL_KES)

    if risk.is_locked:
        print(f"SYSTEM LOCKED: {risk.lock_reason}")
        return

    print("Risk Engine ready.")
    print("Research Engine + Strategy modules loaded.")
    print("Next: feed historical data and run first research backtest.")


if __name__ == "__main__":
    main()
