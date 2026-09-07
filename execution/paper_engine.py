"""
FATE QUANT — Paper Trading Engine

Phase E:
- Real market data
- Real strategy decisions
- Real risk checks
- Zero real money
"""

from typing import Dict, Optional
from loguru import logger

from config.settings import (
    TOTAL_CAPITAL_KES,
    INITIAL_LIVE_ALLOCATION_PCT,
    ALLOWED_SYMBOLS,
    PRIMARY_TIMEFRAME,
    HIGHER_TIMEFRAME,
    ALLOW_LIVE_TRADING,
    SCORE_GATES,
)
from data.data_handler import DataHandler
from risk.risk_engine import RiskEngine
from strategies.trend_momentum_breakout import TrendMomentumBreakout
from execution.paper_broker import PaperBroker
from portfolio.paper_portfolio import PaperPortfolio
from alerts.logger_alerts import AlertBus


class PaperEngine:
    def __init__(self):
        # Only 10% allocation is used even in paper mode,
        # matching the constitution's live-test allocation rule.
        paper_capital = TOTAL_CAPITAL_KES * INITIAL_LIVE_ALLOCATION_PCT
        self.handler = DataHandler()
        self.broker = PaperBroker()
        self.portfolio = PaperPortfolio(starting_cash=paper_capital)
        self.risk = RiskEngine(equity=paper_capital, research_mode=True)
        self.alerts = AlertBus()
        self.last_prices: Dict[str, float] = {}

        if ALLOW_LIVE_TRADING:
            raise RuntimeError("Paper engine must not run with live trading enabled.")

        logger.info(f"Paper engine started. Capital: {paper_capital:.2f} | Live trading: OFF")

    def _refresh_equity(self):
        equity = self.portfolio.mark_to_market(self.last_prices)
        self.risk.update_equity(equity)
        return equity

    def _close_all(self, reason: str):
        for symbol in list(self.portfolio.positions.keys()):
            price = self.last_prices.get(symbol)
            if not price:
                continue
            fill = self.broker.sell(symbol, self.portfolio.positions[symbol].quantity, price, reason)
            trade = self.portfolio.close_long(symbol, fill.fill_price, fill.fee, reason)
            if trade:
                self.risk.update_equity(self._refresh_equity(), trade_pnl=trade.pnl)
                self.alerts.notify(
                    f"CLOSED {symbol} | PnL {trade.pnl:.2f} | {reason}"
                )

    def scan_symbol(self, symbol: str):
        equity = self._refresh_equity()

        if self.risk.check_kill_switch():
            self.alerts.notify(f"KILL SWITCH: {self.risk.lock_reason}")
            self._close_all("Kill Switch")
            return

        htf = self.handler.fetch_ohlcv(symbol, HIGHER_TIMEFRAME, limit=250)
        ptf = self.handler.fetch_ohlcv(symbol, PRIMARY_TIMEFRAME, limit=200)

        if not self.handler.validate_data(htf) or not self.handler.validate_data(ptf):
            self.alerts.notify(f"DATA INVALID: {symbol}")
            return

        last = float(ptf["close"].iloc[-1])
        high = float(ptf["high"].iloc[-1])
        low = float(ptf["low"].iloc[-1])
        self.last_prices[symbol] = last

        # Manage open position first
        if self.portfolio.has_position(symbol):
            pos = self.portfolio.positions[symbol]
            if low <= pos.stop_price:
                fill = self.broker.sell(symbol, pos.quantity, pos.stop_price, "Stop Loss")
                trade = self.portfolio.close_long(symbol, fill.fill_price, fill.fee, "Stop Loss")
                if trade:
                    self.risk.update_equity(self._refresh_equity(), trade_pnl=trade.pnl)
                    self.alerts.notify(f"STOP {symbol} | PnL {trade.pnl:.2f}")
                return
            if high >= pos.take_profit:
                fill = self.broker.sell(symbol, pos.quantity, pos.take_profit, "Take Profit 2R")
                trade = self.portfolio.close_long(symbol, fill.fill_price, fill.fee, "Take Profit 2R")
                if trade:
                    self.risk.update_equity(self._refresh_equity(), trade_pnl=trade.pnl)
                    self.alerts.notify(f"TP {symbol} | PnL {trade.pnl:.2f}")
                return
            return

        # New entries only if no lock and no existing position
        can_trade, reason = self.risk.can_open_trade()
        if not can_trade:
            logger.debug(f"No new trade {symbol}: {reason}")
            return

        strategy = TrendMomentumBreakout(htf, ptf)
        signal = strategy.generate_signal(symbol)

        if not signal.is_valid or signal.score < SCORE_GATES["valid_min"]:
            logger.debug(f"NO TRADE {symbol}: {signal.reason} score={signal.score}")
            return

        size = self.risk.calculate_position_size(signal.entry_price, signal.stop_price)
        if size.rejected or size.quantity <= 0:
            logger.info(f"SIZE REJECTED {symbol}: {size.reason}")
            return

        risk_dist = abs(signal.entry_price - signal.stop_price)
        take_profit = signal.entry_price + (risk_dist * 2.0)

        fill = self.broker.buy(symbol, size.quantity, signal.entry_price, signal.reason)
        opened = self.portfolio.open_long(
            symbol=symbol,
            quantity=size.quantity,
            fill_price=fill.fill_price,
            stop_price=signal.stop_price,
            take_profit=take_profit,
            fee=fill.fee,
        )
        if not opened:
            self.alerts.notify(f"OPEN FAILED {symbol} — insufficient paper cash")
            return

        self._refresh_equity()
        self.alerts.notify(
            f"PAPER OPEN {symbol} qty={size.quantity:.6f} "
            f"entry={fill.fill_price:.4f} stop={signal.stop_price:.4f} "
            f"tp={take_profit:.4f} score={signal.score:.1f}"
        )

    def run_once(self):
        """One scan cycle across the universe."""
        logger.info("Paper scan starting")
        for symbol in ALLOWED_SYMBOLS:
            try:
                self.scan_symbol(symbol)
            except Exception as e:
                self.alerts.notify(f"ERROR {symbol}: {e}")
        equity = self._refresh_equity()
        logger.info(
            f"Equity={equity:.2f} Cash={self.portfolio.cash:.2f} "
            f"Open={self.portfolio.open_count()} Closed={len(self.portfolio.closed)}"
        )
        return {
            "equity": equity,
            "cash": self.portfolio.cash,
            "open": self.portfolio.open_count(),
            "closed": len(self.portfolio.closed),
            "locked": self.risk.is_locked,
            "lock_reason": self.risk.lock_reason,
        }
