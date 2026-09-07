"""
Beginner Binance TESTNET setup.
Writes keys to local .env only. Never uses mainnet.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(ROOT, ".env")


def upsert_env(values: dict):
    existing = {}
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.split("=", 1)
                    existing[k.strip()] = v.strip()
    existing.update(values)
    existing.setdefault("TELEGRAM_BOT_TOKEN", "")
    existing.setdefault("TELEGRAM_CHAT_ID", "")
    existing["ALLOW_LIVE_TRADING"] = "false"
    lines = [
        "# Local secrets. Do not commit.\n",
        f"TELEGRAM_BOT_TOKEN={existing.get('TELEGRAM_BOT_TOKEN', '')}\n",
        f"TELEGRAM_CHAT_ID={existing.get('TELEGRAM_CHAT_ID', '')}\n",
        f"BINANCE_TESTNET_API_KEY={existing.get('BINANCE_TESTNET_API_KEY', '')}\n",
        f"BINANCE_TESTNET_API_SECRET={existing.get('BINANCE_TESTNET_API_SECRET', '')}\n",
        "ALLOW_LIVE_TRADING=false\n",
    ]
    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"Saved {ENV_PATH}")


def main():
    print("FATE QUANT — Binance SPOT TESTNET setup")
    print("Use keys from https://testnet.binance.vision")
    print("Do NOT use real Binance mainnet keys.")
    print()
    key = input("Paste BINANCE_TESTNET_API_KEY: ").strip()
    secret = input("Paste BINANCE_TESTNET_API_SECRET: ").strip()
    if not key or not secret:
        print("Both values are required.")
        return
    upsert_env({
        "BINANCE_TESTNET_API_KEY": key,
        "BINANCE_TESTNET_API_SECRET": secret,
    })

    from dotenv import load_dotenv
    load_dotenv(ENV_PATH, override=True)
    from execution.testnet_broker import TestnetBroker

    broker = TestnetBroker()
    ready, reason = broker.ready()
    if not ready:
        print(f"Saved, but broker not ready: {reason}")
        return
    try:
        usdt = broker.fetch_balance_usdt()
        print(f"Testnet connected. USDT free balance: {usdt}")
        print("This is testnet play money, not your real funds.")
    except Exception as e:
        print(f"Keys saved, but testnet request failed: {e}")
        print("Confirm the keys are from testnet.binance.vision, not live Binance.")


if __name__ == "__main__":
    main()
