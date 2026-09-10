"""
FATE QUANT — Paper Trading Engine
Live public data. Real decisions. Zero real money.
"""

from typing import Dict
from datetime import datetime, timezone
from loguru import logger

from config.settings import (
    TOTAL_CAPITAL_KES,
    INITIAL_LIVE_ALLOCATION_PCT,
    ALLOWED_SYMBOLS,
    PRIMARY_TIMEFRAME,
    HIGHER_TIMEFRAME,
    ALLOW_LIVE_TRADING,
    SCORE_GATES,
    MAX_OPEN_POSITIONS,
    MAX_BARS_IN_TRADE,
)
from data.data_handler import DataHandler
from risk.risk_engine import RiskEngine
from risk.session import DailySession
from strategies.trend_momentum_breakout import TrendMomentumBreakout
from execution.paper_broker import PaperBroker
from portfolio.paper_portfolio import PaperPortfolio
from alerts.logger_alerts import AlertBus
from database.journal import TradeJournal


class PaperEngine:
    def __init__(self):
        paper_capital = TOTAL_CAPITAL_KES * INITIAL_LIVE_ALLOCATION_PCT
        self.handler = DataHandler()
        self.broker = PaperBroker()
        self.portfolio = PaperPortfolio(starting_cash=paper_capital)
        self.risk = RiskEngine(equity=paper_capital, research_mode=True)
        self.session = DailySession(self.risk)
        self.alerts = AlertBus()
        self.journal = TradeJournal("paper_trades.csv")
        self.last_prices: Dict[str, float] = {}

        if ALLOW_LIVE_TRADING:
            raise RuntimeError("Paper engine must not run with live trading enabled.")
        logger.info(f"Paper engine started. Capital: {paper_capital:.2f}")

    def _refresh_equity(self):
        equity = self.portfolio.mark_to_market(self.last_prices)
        self.risk.update_equity(equity)
        return equity

    def _close_position(self, symbol: str, price: float, reason: str):
        pos = self.portfolio.positions.get(symbol)
        if not pos:
            return
        fill = self.broker.sell(symbol, pos.quantity, price, reason)
        trade = self.portfolio.close_long(symbol, fill.fill_price, fill.fee, reason)
        if trade:
            self.risk.update_equity(self._refresh_equity(), trade_pnl=trade.pnl)
            self.journal.write("CLOSE", {
                "symbol": symbol, "side": "sell", "quantity": trade.quantity,
                "price": trade.exit_price, "pnl": trade.pnl, "reason": reason,
            })
            self.alerts.notify(f"CLOSED {symbol} | PnL {trade.pnl:.2f} | {reason}")

    def _close_all(self, reason: str):
        for symbol in list(self.portfolio.positions.keys()):
            price = self.last_prices.get(symbol)
            if price:
                self._close_position(symbol, price, reason)

    def scan_symbol(self, symbol: str):
        self.session.roll()
        if self.risk.check_kill_switch():
            self.alerts.notify(f"KILL SWITCH: {self.risk.lock_reason}")
            self._close_all("Kill Switch")
            return

        htf = self.handler.fetch_ohlcv(symbol, HIGHER_TIMEFRAME, limit=250)
        ptf = self.handler.fetch_ohlcv(symbol, PRIMARY_TIMEFRAME, limit=200)
        if not self.handler.validate_data(htf) or not self.handler.validate_data(ptf):
            print(f"{symbol}: DATA INVALID")
            return

        last = float(ptf["close"].iloc[-1])
        high = float(ptf["high"].iloc[-1])
        low = float(ptf["low"].iloc[-1])
        self.last_prices[symbol] = last

        if self.portfolio.has_position(symbol):
            pos = self.portfolio.positions[symbol]
            hours_held = (datetime.now(timezone.utc) - pos.entry_time).total_seconds() / 3600
            if low <= pos.stop_price:
                self._close_position(symbol, pos.stop_price, "Stop Loss")
            elif high >= pos.take_profit:
                self._close_position(symbol, pos.take_profit, "Take Profit 2R")
            elif hours_held >= MAX_BARS_IN_TRADE:
                self._close_position(symbol, last, "Time Stop")
            else:
                print(f"{symbol}: HOLD price={last:.4f} hours={hours_held:.1f}")
            return

        if self.portfolio.open_count() >= MAX_OPEN_POSITIONS:
            print(f"{symbol}: SKIP max positions already open")
            return

        can_trade, reason = self.risk.can_open_trade()
        if not can_trade:
            print(f"{symbol}: SKIP risk ({reason})")
            return

        signal = TrendMomentumBreakout(htf, ptf).generate_signal(symbol)
        gate = SCORE_GATES["valid_min"]
        print(
            f"{symbol}: score={signal.score:.1f} valid={signal.is_valid} "
            f"price={last:.4f} reason={signal.reason}"
        )
        if not signal.is_valid or signal.score < gate:
            print(f"{symbol}: NO TRADE (need score >= {gate})")
            return

        size = self.risk.calculate_position_size(signal.entry_price, signal.stop_price)
        if size.rejected or size.quantity <= 0:
            print(f"{symbol}: SKIP size rejected ({size.reason})")
            return

        take_profit = signal.entry_price + abs(signal.entry_price - signal.stop_price) * 2.0
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
            self.alerts.notify(f"OPEN FAILED {symbol}")
            return

        self._refresh_equity()
        self.journal.write("OPEN", {
            "symbol": symbol, "side": "buy", "quantity": size.quantity,
            "price": fill.fill_price, "stop": signal.stop_price,
            "take_profit": take_profit, "score": signal.score, "reason": signal.reason,
        })
        self.alerts.notify(
            f"PAPER OPEN {symbol} qty={size.quantity:.6f} entry={fill.fill_price:.4f} "
            f"score={signal.score:.1f}"
        )

    def run_once(self):
        logger.info("Paper scan starting")
        for symbol in ALLOWED_SYMBOLS:
            try:
                self.scan_symbol(symbol)
            except Exception as e:
                self.alerts.notify(f"ERROR {symbol}: {e}")
                print(f"{symbol}: ERROR {e}")
        equity = self._refresh_equity()
        return {
            "equity": equity,
            "cash": self.portfolio.cash,
            "open": self.portfolio.open_count(),
            "closed": len(self.portfolio.closed),
            "locked": self.risk.is_locked,
            "lock_reason": self.risk.lock_reason,
        }
