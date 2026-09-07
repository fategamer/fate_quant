# FATE QUANT V1.0

Risk-first crypto **spot** system. Default state: **NO TRADE**.

## Constitution

- BTC/USDT, ETH/USDT, SOL/USDT only
- Binance Spot
- Capital: KES 10,000
- First allocation: 10%
- Risk/trade: 0.25%
- Max daily loss: 1%
- Max drawdown: 5%
- No leverage, no martingale, no grid, no memecoins
- Live/mainnet trading locked until all gates pass

## Roadmap

- A Rules ✅
- B Backtester ✅
- C Costs ✅
- D OOS + walk-forward ✅
- E Paper trading ✅
- F Testnet ✅ framework ready
- G Micro-live (real funds, 10% only) — locked
- H Scale — locked

## Commands

```bash
pip install -r requirements.txt

python scripts/run_research.py
python scripts/run_walk_forward.py
python scripts/run_paper.py

# Phase F — testnet keys required in .env
cp config/secrets.example.env .env
python scripts/run_testnet.py
```

Get testnet keys only from Binance Spot Testnet (`testnet.binance.vision`).
Do not put mainnet keys in `.env`.
