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
Protect capital first.  
Trade only when a measurable statistical edge exists.  
Cut invalid trades according to predefined rules.  
Never exceed the risk budget.  
Stop when conditions become abnormal.  
Compound only after performance has been demonstrated.

---

## Development Phases

- **PHASE A** — Research (mathematics & rules)
- **PHASE B** — Backtester
- **PHASE C** — Reality check (fees, spread, slippage)
- **PHASE D** — Out-of-sample testing
- **PHASE E** — Paper trading
- **PHASE F** — Testnet
- **PHASE G** — Micro-live
- **PHASE H** — Controlled scaling

Fail any gate → Do not deploy.

---

## Current Status

- Repository structure: Complete
- Constitution locked in `config/settings.py`
- Risk Engine with Kill Switch: Implemented
- Deterministic Trend + Momentum + Breakout strategy (long-only): Implemented
- Research Engine (backtester) skeleton with full metrics: Implemented
- Data Handler: Implemented

**Next priority:** Make the Research Engine fully functional so we can answer:

> “If I had run these exact rules historically, what would have happened after realistic costs?”
