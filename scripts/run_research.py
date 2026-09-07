"""
FATE QUANT — Research Runner

Fetches recent historical data and runs the Research Engine.
This is PHASE B work: we want evidence, not hope.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.data_handler import DataHandler
from backtesting.research_engine import ResearchEngine
from config.settings import ALLOWED_SYMBOLS, PRIMARY_TIMEFRAME, HIGHER_TIMEFRAME, TOTAL_CAPITAL_KES


def run_single_symbol(symbol: str, limit: int = 1000):
    print(f"\n{'='*60}")
    print(f"Researching: {symbol}")
    print(f"{'='*60}")

    handler = DataHandler()

    print("Fetching higher timeframe data...")
    htf = handler.fetch_ohlcv(symbol, HIGHER_TIMEFRAME, limit=500)
    print(f"  HTF bars: {len(htf)}")

    print("Fetching primary timeframe data...")
    ptf = handler.fetch_ohlcv(symbol, PRIMARY_TIMEFRAME, limit=limit)
    print(f"  PTF bars: {len(ptf)}")

    if not handler.validate_data(htf) or not handler.validate_data(ptf):
        print("Data validation failed.")
        return None

    engine = ResearchEngine(initial_capital=TOTAL_CAPITAL_KES)
    report = engine.run_bar_by_bar(symbol, htf, ptf)

    print(report.summary())

    if report.trades:
        print("\nLast 5 trades:")
        for t in report.trades[-5:]:
            print(f"  {t.entry_time.date()} → {t.exit_time.date()} | "
                  f"PnL: {t.pnl:.2f} | Reason: {t.exit_reason}")

    return report


def main():
    print("FATE QUANT V1 — Research Engine")
    print("Mission: Protect capital first. Only trade with measurable edge.")
    print(f"Capital under test: KES {TOTAL_CAPITAL_KES:,}")
    print("Live trading: DISABLED")
    print()

    results = {}
    for symbol in ALLOWED_SYMBOLS:
        try:
            report = run_single_symbol(symbol, limit=800)
            if report:
                results[symbol] = report
        except Exception as e:
            print(f"Error on {symbol}: {e}")

    print("\n" + "="*60)
    print("RESEARCH SUMMARY")
    print("="*60)
    for symbol, report in results.items():
        status = "INTERESTING" if report.max_drawdown_pct < 15 and report.total_return_pct > 0 else "NEEDS WORK"
        print(f"{symbol}: Return {report.total_return_pct:.1f}% | DD {report.max_drawdown_pct:.1f}% | "
              f"Trades {report.total_trades} | {status}")


if __name__ == "__main__":
    main()
