# FATE QUANT V1.0

**Risk-first crypto spot trading system**

## Mission

Find statistically defensible opportunities while making catastrophic loss structurally difficult.

The bot’s default state is: **NO TRADE**

---

## Constitution (Non-negotiable)

| Rule                        | Value                          |
|----------------------------|--------------------------------|
| Market                     | Crypto Spot only               |
| Pairs                      | BTC/USDT, ETH/USDT, SOL/USDT   |
| Exchange                   | Binance Spot (+ Testnet)       |
| Total Capital              | KES 10,000                     |
| Initial Live Allocation    | 10% (KES 1,000)                |
| Risk per trade             | 0.25% (KES 25)                 |
| Max Daily Loss             | 1% (KES 100)                   |
| Max Account Drawdown       | 5% (KES 500)                   |
| Leverage                   | 0× (Spot only)                 |
| Martingale                 | Prohibited                     |
| Grid                       | Prohibited                     |
| Memecoins                  | Prohibited                     |
| Live trading               | Forbidden until Gates pass     |

**Primary Directive**  
Protect capital first. Trade only when a measurable statistical edge exists. Cut invalid trades according to predefined rules. Never exceed the risk budget. Stop when conditions become abnormal. Compound only after performance has been demonstrated.

---

## Roadmap

- **PHASE A** — Research rules ✅
- **PHASE B** — Backtester ✅
- **PHASE C** — Reality check (fees/slippage) ✅
- **PHASE D** — Out-of-sample + walk-forward ✅ framework ready
- **PHASE E** — Paper trading
- **PHASE F** — Testnet
- **PHASE G** — Micro-live
- **PHASE H** — Controlled scaling

Fail any gate → Do not deploy.

---

## How to run

```bash
pip install -r requirements.txt

# Phase B/C — portfolio research
python scripts/run_research.py

# Phase D — out-of-sample + walk-forward
python scripts/run_walk_forward.py
```

---

## Current Status

Phase D framework is implemented.

**Next on the roadmap:** Phase E paper-trading engine (real-time data, zero real money).
