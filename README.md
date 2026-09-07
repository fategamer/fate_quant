# FATE QUANT V1.0

Risk-first Binance **spot** system. Default state: **NO TRADE**.

## Constitution

- Universe: BTC/USDT, ETH/USDT, SOL/USDT
- Capital: KES 10,000
- First allocation: 10%
- Risk/trade: 0.25%
- Max daily loss: 1%
- Max drawdown: 5%
- Max open positions: 1
- No leverage, martingale, grid, or memecoins
- Live/mainnet trading locked

## Roadmap

- A Rules ✅
- B Backtester ✅
- C Costs ✅
- D OOS + walk-forward ✅
- E Paper ✅
- F Testnet ✅
- Quality: look-ahead fix, regime engine, weighted scoring, journal ✅
- G Micro-live — locked
- H Scale — locked

## Commands

```bash
pip install -r requirements.txt
python -m pytest tests/ -q
python scripts/run_gates.py
python scripts/run_paper.py
```

Testnet (testnet keys only in `.env`):

```bash
cp config/secrets.example.env .env
python scripts/run_testnet.py
```
