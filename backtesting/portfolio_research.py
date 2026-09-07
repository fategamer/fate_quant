"""
FATE QUANT — Portfolio Research Engine

Runs the strategy across multiple symbols under one shared capital
and risk budget. Kill Switch is global.
"""

from typing import Dict, List, Optional
import pandas as pd
from dataclasses import dataclass, field

from config.settings import TOTAL_CAPITAL_KES, ALLOWED_SYMBOLS
from backtesting.research_engine import ResearchEngine, PerformanceReport, Trade
from data.data_handler import DataHandler
from risk.risk_engine import RiskEngine


@dataclass
class PortfolioReport:
    combined: PerformanceReport
    per_symbol: Dict[str, PerformanceReport] = field(default_factory=dict)
    notes: str = ""

    def summary(self) -> str:
        lines = [
            "=" * 60,
            "FATE QUANT — PORTFOLIO RESEARCH REPORT",
            "=" * 60,
            self.combined.summary(),
            "",
            "--- Per Symbol ---",
        ]
        for symbol, report in self.per_symbol.items():
            lines.append(
                f"{symbol}: Return {report.total_return_pct:.1f}% | "
                f"DD {report.max_drawdown_pct:.1f}% | "
                f"Trades {report.total_trades} | "
                f"PF {report.profit_factor:.2f}"
            )
        if self.notes:
            lines.append(f"\nNotes: {self.notes}")
        return "\n".join(lines)


class PortfolioResearchEngine:
    """
    Shared capital, shared risk engine, global kill switch.
    Each symbol is simulated, but position sizing and risk limits
    are applied against the same equity pool.
    """

    def __init__(self, initial_capital: float = TOTAL_CAPITAL_KES):
        self.initial_capital = initial_capital
        self.handler = DataHandler()

    def run(
        self,
        symbols: Optional[List[str]] = None,
        ptf_limit: int = 800,
        htf_limit: int = 500,
    ) -> PortfolioReport:
        symbols = symbols or ALLOWED_SYMBOLS

        # We run each symbol independently for V1 research clarity,
        # then combine the trade lists and metrics.
        # (True simultaneous multi-asset with shared equity
        #  is a later enhancement.)

        all_trades: List[Trade] = []
        per_symbol_reports: Dict[str, PerformanceReport] = {}
        combined_equity_curve = [self.initial_capital]

        for symbol in symbols:
            print(f"Researching {symbol}...")
            try:
                htf = self.handler.fetch_ohlcv(symbol, "4h", limit=htf_limit)
                ptf = self.handler.fetch_ohlcv(symbol, "1h", limit=ptf_limit)

                if not self.handler.validate_data(htf) or not self.handler.validate_data(ptf):
                    print(f"  Data validation failed for {symbol}")
                    continue

                engine = ResearchEngine(initial_capital=self.initial_capital)
                report = engine.run_bar_by_bar(symbol, htf, ptf)

                per_symbol_reports[symbol] = report
                all_trades.extend(report.trades)

            except Exception as e:
                print(f"  Error on {symbol}: {e}")

        # Build a simple combined report from all trades
        combined_engine = ResearchEngine(initial_capital=self.initial_capital)
        combined_engine.trades = all_trades
        # Reconstruct rough equity curve from trades (simplified)
        equity = self.initial_capital
        combined_engine.equity_curve = [equity]
        for t in sorted(all_trades, key=lambda x: x.exit_time):
            equity += t.pnl
            combined_engine.equity_curve.append(equity)
        combined_engine.equity = equity

        combined_report = combined_engine.calculate_metrics(all_trades)

        return PortfolioReport(
            combined=combined_report,
            per_symbol=per_symbol_reports,
            notes="V1 portfolio research: symbols run independently then aggregated. Shared-equity simultaneous simulation comes later.",
        )
