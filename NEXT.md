# FATE QUANT — What is next

## Done
A rules, B backtester, C costs, D OOS/walk-forward, E paper, F testnet.
Look-ahead fix, regime engine, weighted scoring, journal, max 1 position, tests.

## Not done / blocked
G micro-live and H scale are locked until evidence exists.

## Immediate next (you)
Run on your machine and save the output:

```bash
pip install -r requirements.txt
python -m pytest tests/ -q
python scripts/run_gates.py
python scripts/run_paper.py --loops 1
```

Paste the reports here. That decides whether we harden the strategy or keep it.

## Immediate next (engineering)
Only after numbers:
1. Review profit factor, max DD, trade count, OOS verdict
2. If weak/fail: tighten filters or change exits — do not go live
3. If interesting: longer paper run, then testnet
4. Live 10% allocation only after paper + testnet survive

## What we will not do next
- Enable ALLOW_LIVE_TRADING
- Connect KES 10,000
- Add leverage, grid, martingale, or memecoins
