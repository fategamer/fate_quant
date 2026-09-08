"""
FATE QUANT — Phase D: Out-of-Sample + Walk-Forward Testing
"""

from dataclasses import dataclass, field
from typing import List, Optional
import time
import pandas as pd

from config.settings import TOTAL_CAPITAL_KES, ALLOWED_SYMBOLS, PRIMARY_TIMEFRAME, HIGHER_TIMEFRAME
from data.data_handler import DataHandler
from backtesting.research_engine import ResearchEngine, PerformanceReport


@dataclass
class SplitReport:
    symbol: str
    in_sample: PerformanceReport
    out_of_sample: PerformanceReport
    verdict: str

    def summary(self) -> str:
        return (
            f"{self.symbol}\n"
            f"  IS  : Return {self.in_sample.total_return_pct:.2f}% | "
            f"DD {self.in_sample.max_drawdown_pct:.2f}% | "
            f"Trades {self.in_sample.total_trades} | "
            f"PF {self.in_sample.profit_factor:.2f}\n"
            f"  OOS : Return {self.out_of_sample.total_return_pct:.2f}% | "
            f"DD {self.out_of_sample.max_drawdown_pct:.2f}% | "
            f"Trades {self.out_of_sample.total_trades} | "
            f"PF {self.out_of_sample.profit_factor:.2f}\n"
            f"  Verdict: {self.verdict}"
        )


@dataclass
class WalkForwardFold:
    fold: int
    train_start: str
    train_end: str
    test_start: str
    test_end: str
    test_report: PerformanceReport


@dataclass
class WalkForwardReport:
    symbol: str
    folds: List[WalkForwardFold] = field(default_factory=list)
    avg_test_return: float = 0.0
    avg_test_dd: float = 0.0
    avg_test_pf: float = 0.0
    passing_folds: int = 0
    verdict: str = ""

    def summary(self) -> str:
        lines = [
            "=" * 60,
            f"WALK-FORWARD REPORT — {self.symbol}",
            "=" * 60,
        ]
        for f in self.folds:
            r = f.test_report
            lines.append(
                f"Fold {f.fold}: {f.test_start} → {f.test_end} | "
                f"Ret {r.total_return_pct:.2f}% | DD {r.max_drawdown_pct:.2f}% | "
                f"PF {r.profit_factor:.2f} | Trades {r.total_trades}"
            )
        lines += [
            "-" * 60,
            f"Avg test return     : {self.avg_test_return:.2f}%",
            f"Avg test drawdown   : {self.avg_test_dd:.2f}%",
            f"Avg test PF         : {self.avg_test_pf:.2f}",
            f"Passing folds       : {self.passing_folds}/{len(self.folds)}",
            f"Verdict             : {self.verdict}",
            "=" * 60,
        ]
        return "\n".join(lines)


def _verdict(is_report: PerformanceReport, oos_report: PerformanceReport) -> str:
    if oos_report.total_trades < 3:
        return "INCONCLUSIVE — too few OOS trades"
    if oos_report.max_drawdown_pct >= 15:
        return "FAIL — OOS drawdown too large"
    if oos_report.profit_factor < 1.0 and oos_report.total_return_pct < 0:
        return "FAIL — OOS negative expectancy"
    if is_report.total_return_pct > 20 and oos_report.total_return_pct < 0:
        return "FAIL — likely overfitting (IS good, OOS bad)"
    if oos_report.profit_factor >= 1.1 and oos_report.max_drawdown_pct < 10:
        return "INTERESTING — OOS survives"
    return "WEAK — not enough evidence to deploy"


def _wf_verdict(report: WalkForwardReport) -> str:
    if len(report.folds) == 0:
        return "INCONCLUSIVE — no folds"
    pass_rate = report.passing_folds / len(report.folds)
    if pass_rate >= 0.6 and report.avg_test_pf >= 1.1 and report.avg_test_dd < 12:
        return "INTERESTING — walk-forward holds"
    if pass_rate < 0.4 or report.avg_test_pf < 1.0:
        return "FAIL — walk-forward does not hold"
    return "WEAK — mixed walk-forward results"


class OutOfSampleTester:
    def __init__(self, initial_capital: float = TOTAL_CAPITAL_KES):
        self.initial_capital = initial_capital
        self.handler = DataHandler()

    def split_frames(self, df: pd.DataFrame, is_ratio: float = 0.70):
        if df is None or df.empty:
            return df, df
        split_idx = max(int(len(df) * is_ratio), 80)
        if split_idx >= len(df) - 20:
            split_idx = max(len(df) // 2, 60)
        return df.iloc[:split_idx].copy(), df.iloc[split_idx:].copy()

    def run_symbol(
        self,
        symbol: str,
        ptf_limit: int = 800,
        htf_limit: int = 500,
        is_ratio: float = 0.70,
    ) -> Optional[SplitReport]:
        htf = self.handler.fetch_ohlcv(symbol, HIGHER_TIMEFRAME, limit=htf_limit)
        time.sleep(0.4)
        ptf = self.handler.fetch_ohlcv(symbol, PRIMARY_TIMEFRAME, limit=ptf_limit)
        if not self.handler.validate_data(htf) or not self.handler.validate_data(ptf):
            print(f"  Invalid data for {symbol}")
            return None
        if len(ptf) < 120:
            print(f"  Not enough bars for {symbol}")
            return None

        htf_is, htf_oos = self.split_frames(htf, is_ratio)
        ptf_is, ptf_oos = self.split_frames(ptf, is_ratio)

        is_report = ResearchEngine(self.initial_capital).run_bar_by_bar(symbol, htf_is, ptf_is)
        oos_report = ResearchEngine(self.initial_capital).run_bar_by_bar(symbol, htf_oos, ptf_oos)
        return SplitReport(symbol, is_report, oos_report, _verdict(is_report, oos_report))

    def run_all(self) -> List[SplitReport]:
        results = []
        for symbol in ALLOWED_SYMBOLS:
            print(f"OOS test: {symbol}")
            try:
                report = self.run_symbol(symbol)
                if report:
                    results.append(report)
                    print(report.summary())
            except Exception as e:
                print(f"  Error on {symbol}: {e}")
        return results


class WalkForwardTester:
    def __init__(self, initial_capital: float = TOTAL_CAPITAL_KES):
        self.initial_capital = initial_capital
        self.handler = DataHandler()

    def run_symbol(
        self,
        symbol: str,
        ptf_limit: int = 800,
        n_folds: int = 3,
        test_ratio: float = 0.20,
    ) -> Optional[WalkForwardReport]:
        htf = self.handler.fetch_ohlcv(symbol, HIGHER_TIMEFRAME, limit=400)
        time.sleep(0.4)
        ptf = self.handler.fetch_ohlcv(symbol, PRIMARY_TIMEFRAME, limit=ptf_limit)
        if not self.handler.validate_data(htf) or not self.handler.validate_data(ptf):
            return None
        if len(ptf) < 200:
            return None

        test_size = max(int(len(ptf) * test_ratio), 60)
        train_min = 100
        folds: List[WalkForwardFold] = []

        for fold in range(1, n_folds + 1):
            train_end = train_min + (fold - 1) * test_size
            test_end = train_end + test_size
            if test_end > len(ptf):
                break
            ptf_train = ptf.iloc[:train_end]
            ptf_test = ptf.iloc[train_end:test_end]
            if ptf_test.empty or ptf_train.empty:
                continue

            htf_test = htf[htf.index <= ptf_test.index[-1]]
            if len(htf_test) < 50:
                htf_test = htf.copy()

            test_report = ResearchEngine(self.initial_capital).run_bar_by_bar(
                symbol, htf_test, ptf_test
            )
            folds.append(
                WalkForwardFold(
                    fold=fold,
                    train_start=str(ptf_train.index[0].date()),
                    train_end=str(ptf_train.index[-1].date()),
                    test_start=str(ptf_test.index[0].date()),
                    test_end=str(ptf_test.index[-1].date()),
                    test_report=test_report,
                )
            )

        report = WalkForwardReport(symbol=symbol, folds=folds)
        if folds:
            report.avg_test_return = sum(f.test_report.total_return_pct for f in folds) / len(folds)
            report.avg_test_dd = sum(f.test_report.max_drawdown_pct for f in folds) / len(folds)
            report.avg_test_pf = sum(f.test_report.profit_factor for f in folds) / len(folds)
            report.passing_folds = sum(
                1 for f in folds
                if f.test_report.profit_factor >= 1.0 and f.test_report.max_drawdown_pct < 15
            )
        report.verdict = _wf_verdict(report)
        return report

    def run_all(self) -> List[WalkForwardReport]:
        results = []
        for symbol in ALLOWED_SYMBOLS:
            print(f"Walk-forward: {symbol}")
            try:
                report = self.run_symbol(symbol)
                if report:
                    results.append(report)
                    print(report.summary())
            except Exception as e:
                print(f"  Error on {symbol}: {e}")
        return results
