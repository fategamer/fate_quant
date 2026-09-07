"""
FATE QUANT V1.0 — Global Configuration
This file contains the constitution. Strategies cannot override these values.
"""

# === CAPITAL & RISK (CONSTITUTION) ===
TOTAL_CAPITAL_KES = 10_000
INITIAL_LIVE_ALLOCATION_PCT = 0.10          # 10% only
RISK_PER_TRADE_PCT = 0.0025                 # 0.25%
MAX_DAILY_LOSS_PCT = 0.01                   # 1%
MAX_DRAWDOWN_PCT = 0.05                     # 5%

# Calculated absolute values (based on total capital)
RISK_PER_TRADE_KES = TOTAL_CAPITAL_KES * RISK_PER_TRADE_PCT          # 25
MAX_DAILY_LOSS_KES = TOTAL_CAPITAL_KES * MAX_DAILY_LOSS_PCT          # 100
MAX_DRAWDOWN_KES = TOTAL_CAPITAL_KES * MAX_DRAWDOWN_PCT              # 500
INITIAL_LIVE_CAPITAL_KES = TOTAL_CAPITAL_KES * INITIAL_LIVE_ALLOCATION_PCT  # 1000

# === MARKET ===
EXCHANGE = "binance"
MARKET_TYPE = "spot"                        # No leverage
ALLOWED_SYMBOLS = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]

# === PROHIBITIONS ===
ALLOW_LEVERAGE = False
ALLOW_MARTINGALE = False
ALLOW_GRID = False
ALLOW_MEMECOINS = False
ALLOW_LIVE_TRADING = False                  # Locked until Gates pass

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

# === KILL SWITCH ===
KILL_SWITCH = {
    "daily_loss_pct": 0.01,
    "max_drawdown_pct": 0.05,
    # Additional triggers can be added later (consecutive losses, etc.)
}
