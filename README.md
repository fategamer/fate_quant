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
| Live trading               | Forbidden until Gates 1–5 pass |

**Primary Directive**  
Protect capital first.  
Trade only when a measurable statistical edge exists.  
Cut invalid trades according to predefined rules.  
Never exceed the risk budget.  
Stop when conditions become abnormal.  
Compound only after performance has been demonstrated.

---

## Testing Gates (Mandatory)

1. Historical backtest  
2. Transaction costs + slippage simulation  
3. Out-of-sample testing  
4. Walk-forward testing  
5. Paper trading  
6. Tiny live deployment  
7. Performance review  
8. Controlled scaling  

Fail any gate → Do not deploy.

---

## Architecture Pipeline

```
MARKET DATA
    ↓
DATA VALIDATOR
    ↓
REGIME ENGINE
    ↓
SIGNAL ENGINE
    ↓
RISK ENGINE  ←— KILL SWITCH (highest authority)
    ↓
POSITION SIZE
    ↓
EXECUTION
    ↓
POSITION MONITOR
    ↓
PERFORMANCE
```

---

## Scoring Model

| Factor            | Weight |
|-------------------|--------|
| Trend             | 20%    |
| Market Structure  | 20%    |
| Momentum          | 15%    |
| Volatility        | 15%    |
| Volume            | 10%    |
| Liquidity         | 10%    |
| Regime            | 10%    |

**Score Gates**
- 0–69  → NO TRADE
- 70–79  → WATCH
- 80–89  → VALID TRADE
- 90–100 → HIGH-CONFIDENCE TRADE

High score does **not** increase risk size. Risk remains fixed at 0.25%.
