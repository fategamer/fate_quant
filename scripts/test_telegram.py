"""
Send one test message to Telegram.
Requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from alerts.telegram import TelegramSender


def main():
    sender = TelegramSender()
    if not sender.enabled:
        print("Telegram not configured.")
        print("Add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to .env")
        print("Create a bot via @BotFather, then message the bot and get your chat id.")
        return
    ok = sender.send("Test alert. Paper/testnet only. Live trading is locked.")
    print("Sent" if ok else "Failed to send")


if __name__ == "__main__":
    main()
