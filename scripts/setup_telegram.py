"""
Beginner Telegram setup.
Run this on your computer. It creates .env and sends one test message.
Do not run this in a public chat. Do not commit .env.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(ROOT, ".env")


def write_env(token: str, chat_id: str):
    existing = {}
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.split("=", 1)
                    existing[k.strip()] = v.strip()
    existing["TELEGRAM_BOT_TOKEN"] = token.strip()
    existing["TELEGRAM_CHAT_ID"] = chat_id.strip()
    existing.setdefault("ALLOW_LIVE_TRADING", "false")
    existing.setdefault("BINANCE_TESTNET_API_KEY", existing.get("BINANCE_TESTNET_API_KEY", ""))
    existing.setdefault("BINANCE_TESTNET_API_SECRET", existing.get("BINANCE_TESTNET_API_SECRET", ""))

    lines = [
        "# Local secrets. Do not commit this file.\n",
        f"TELEGRAM_BOT_TOKEN={existing['TELEGRAM_BOT_TOKEN']}\n",
        f"TELEGRAM_CHAT_ID={existing['TELEGRAM_CHAT_ID']}\n",
        f"BINANCE_TESTNET_API_KEY={existing.get('BINANCE_TESTNET_API_KEY', '')}\n",
        f"BINANCE_TESTNET_API_SECRET={existing.get('BINANCE_TESTNET_API_SECRET', '')}\n",
        f"ALLOW_LIVE_TRADING={existing.get('ALLOW_LIVE_TRADING', 'false')}\n",
    ]
    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"Saved {ENV_PATH}")


def main():
    print("FATE QUANT — Telegram setup")
    print("Token stays on this computer only.")
    print()
    token = input("Paste TELEGRAM_BOT_TOKEN: ").strip()
    chat_id = input("Paste TELEGRAM_CHAT_ID: ").strip()
    if not token or not chat_id:
        print("Both values are required.")
        return
    write_env(token, chat_id)

    from dotenv import load_dotenv
    load_dotenv(ENV_PATH, override=True)
    from alerts.telegram import TelegramSender

    sender = TelegramSender()
    if not sender.enabled:
        print("Setup saved, but Telegram sender is not enabled. Check the values.")
        return
    ok = sender.send("Telegram connected to FATE QUANT. Live trading is locked.")
    print("Test message sent. Check Telegram." if ok else "Saved, but test message failed.")


if __name__ == "__main__":
    main()
