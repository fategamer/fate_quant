"""
FATE QUANT V1.0 — Global Configuration
Constitution. Strategies cannot override these values.
"""

# === CAPITAL & RISK ===
TOTAL_CAPITAL_KES = 10_000
INITIAL_LIVE_ALLOCATION_PCT = 0.10
RISK_PER_TRADE_PCT = 0.0025
MAX_DAILY_LOSS_PCT = 0.01
MAX_DRAWDOWN_PCT = 0.05
MAX_OPEN_POSITIONS = 1                      # one position at a time in V1

RISK_PER_TRADE_KES = TOTAL_CAPITAL_KES * RISK_PER_TRADE_PCT
MAX_DAILY_LOSS_KES = TOTAL_CAPITAL_KES * MAX_DAILY_LOSS_PCT
MAX_DRAWDOWN_KES = TOTAL_CAPITAL_KES * MAX_DRAWDOWN_PCT
INITIAL_LIVE_CAPITAL_KES = TOTAL_CAPITAL_KES * INITIAL_LIVE_ALLOCATION_PCT

# === MARKET ===
EXCHANGE = "binance"
MARKET_TYPE = "spot"
ALLOWED_SYMBOLS = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]

# === PROHIBITIONS ===
ALLOW_LEVERAGE = False
ALLOW_MARTINGALE = False
ALLOW_GRID = False
ALLOW_MEMECOINS = False
ALLOW_LIVE_TRADING = False

# === TIMEFRAMES ===
HIGHER_TIMEFRAME = "4h"
PRIMARY_TIMEFRAME = "1h"

# === SCORING ===
SCORE_WEIGHTS = {
    "trend": 0.20,
    "market_structure": 0.20,
    "momentum": 0.15,
    "volatility": 0.15,
    "volume": 0.10,
    "liquidity": 0.10,
    "regime": 0.10,
}

SCORE_GATES = {
    "no_trade_max": 69,
    "watch_max": 79,
    "valid_min": 80,
    "high_confidence_min": 90,
}

# === COSTS ===
TAKER_FEE = 0.001
MAKER_FEE = 0.001
SLIPPAGE_PCT = 0.0005

# === KILL SWITCH ===
KILL_SWITCH = {
    "daily_loss_pct": 0.01,
    "max_drawdown_pct": 0.05,
    "max_consecutive_losses": 5,
}

# === JOURNAL ===
JOURNAL_DIR = "database/journal"
