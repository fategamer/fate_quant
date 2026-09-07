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
- Time-stop: 48 x 1h bars
- No leverage, martingale, grid, or memecoins
- Live/mainnet trading locked

## Commands

```bash
pip install -r requirements.txt
python -m pytest tests/ -q
python scripts/run_gates.py
python scripts/run_paper.py
```

### Telegram alerts (optional)

1. Create a bot with BotFather and copy the token
2. Message your bot, then get your chat id
3. Put both in `.env`:

```bash
cp config/secrets.example.env .env
# fill TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID
python scripts/test_telegram.py
```

If those vars are missing, the system still runs and only logs alerts.
