"""
FATE QUANT — Testnet Engine
Same decision stack as paper mode.
Orders go to Binance Spot TESTNET only.
"""

from typing import Dict
from datetime import datetime, timezone
from loguru import logger

from config.settings import (
    ALLOWED_SYMBOLS,
    PRIMARY_TIMEFRAME,
    HIGHER_TIMEFRAME,
    ALLOW_LIVE_TRADING,
    SCORE_GATES,
    TOTAL_CAPITAL_KES,
    INITIAL_LIVE_ALLOCATION_PCT,
    MAX_OPEN_POSITIONS,
    MAX_BARS_IN_TRADE,
)
from data.data_handler import DataHandler
from risk.risk_engine import RiskEngine
from risk.session import DailySession
from strategies.trend_momentum_breakout import TrendMomentumBreakout
from execution.testnet_broker import TestnetBroker
from alerts.logger_alerts import AlertBus
from portfolio.paper_portfolio import PaperPortfolio


class TestnetEngine:
    def __init__(self):
        if ALLOW_LIVE_TRADING:
            raise RuntimeError("Refuse to start: ALLOW_LIVE_TRADING is True.")

        self.handler = DataHandler()
        self.broker = TestnetBroker()
        ready, reason = self.broker.ready()
        if not ready:
            raise RuntimeError(f"Testnet broker not ready: {reason}")

        allocated = TOTAL_CAPITAL_KES * INITIAL_LIVE_ALLOCATION_PCT
        self.risk = RiskEngine(equity=allocated, research_mode=True)
        self.session = DailySession(self.risk)
        self.portfolio = PaperPortfolio(starting_cash=allocated)
        self.alerts = AlertBus()
        self.last_prices: Dict[str, float] = {}
        logger.info("Testnet engine started. Mainnet disabled.")

    def _refresh(self):
        equity = self.portfolio.mark_to_market(self.last_prices)
        self.risk.update_equity(equity)
        return equity

    def scan_symbol(self, symbol: str):
        self.session.roll()
        if self.risk.check_kill_switch():
            self.alerts.notify(f"KILL SWITCH: {self.risk.lock_reason}")
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

        if self.portfolio.has_position(symbol):
            pos = self.portfolio.positions[symbol]
            hours_held = (datetime.now(timezone.utc) - pos.entry_time).total_seconds() / 3600
            if low <= pos.stop_price:
                reason = "Stop Loss"
            elif high >= pos.take_profit:
                reason = "Take Profit 2R"
            elif hours_held >= MAX_BARS_IN_TRADE:
                reason = "Time Stop"
            else:
                return
            fill = self.broker.market_sell(symbol, pos.quantity)
            trade = self.portfolio.close_long(symbol, fill.price or last, 0.0, reason)
            if trade:
                self.risk.update_equity(self._refresh(), trade_pnl=trade.pnl)
                self.alerts.notify(
                    f"TESTNET CLOSE {symbol} {reason} id={fill.order_id} pnl={trade.pnl:.2f}"
                )
            return

        if self.portfolio.open_count() >= MAX_OPEN_POSITIONS:
            return

        can_trade, reason = self.risk.can_open_trade()
        if not can_trade:
            return

        signal = TrendMomentumBreakout(htf, ptf).generate_signal(symbol)
        if not signal.is_valid or signal.score < SCORE_GATES["valid_min"]:
            return

        size = self.risk.calculate_position_size(signal.entry_price, signal.stop_price)
        if size.rejected or size.quantity <= 0:
            return

        take_profit = signal.entry_price + abs(signal.entry_price - signal.stop_price) * 2.0
        fill = self.broker.market_buy(symbol, size.quantity)
        opened = self.portfolio.open_long(
            symbol=symbol,
            quantity=fill.quantity or size.quantity,
            fill_price=fill.price or signal.entry_price,
            stop_price=signal.stop_price,
            take_profit=take_profit,
            fee=0.0,
        )
        if opened:
            self._refresh()
            self.alerts.notify(
                f"TESTNET OPEN {symbol} qty={fill.quantity} price={fill.price} id={fill.order_id}"
            )

    def run_once(self):
        logger.info("Testnet scan starting")
        for symbol in ALLOWED_SYMBOLS:
            try:
                self.scan_symbol(symbol)
            except Exception as e:
                self.alerts.notify(f"TESTNET ERROR {symbol}: {e}")
        equity = self._refresh()
        return {
            "equity": equity,
            "cash": self.portfolio.cash,
            "open": self.portfolio.open_count(),
            "closed": len(self.portfolio.closed),
            "locked": self.risk.is_locked,
            "lock_reason": self.risk.lock_reason,
        }
