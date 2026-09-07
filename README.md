# FATE QUANT V1.0

**Risk-first crypto spot trading system**

Default state: **NO TRADE**

## Constitution

- Market: Binance Spot only
- Universe: BTC/USDT, ETH/USDT, SOL/USDT
- Capital: KES 10,000
- Paper / first live allocation: 10% only
- Risk per trade: 0.25%
- Max daily loss: 1%
- Max drawdown: 5%
- Leverage / martingale / grid / memecoins: prohibited
- Live trading: locked until gates pass

## Roadmap

- PHASE A Research rules ✅
- PHASE B Backtester ✅
- PHASE C Fees + slippage ✅
- PHASE D Out-of-sample + walk-forward ✅
- PHASE E Paper trading ✅ framework ready
- PHASE F Testnet
- PHASE G Micro-live
- PHASE H Scale

## Commands

```bash
pip install -r requirements.txt

# Research / portfolio backtest
python scripts/run_research.py

# Out-of-sample + walk-forward
python scripts/run_walk_forward.py

# Paper trading — one scan
python scripts/run_paper.py

# Paper trading — 10 cycles, 60s apart
python scripts/run_paper.py --loops 10 --sleep 60
```

Paper mode uses live public market data and the same risk engine.
It never sends real orders.
