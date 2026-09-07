"""
FATE QUANT — Telegram sender
Optional. If token/chat id missing, this does nothing.
Never logs the token.
"""

import os
import requests
from loguru import logger


class TelegramSender:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
        self.enabled = bool(self.token and self.chat_id)
        if self.enabled:
            logger.info("Telegram alerts enabled")
        else:
            logger.info("Telegram alerts disabled (missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID)")

    def send(self, message: str):
        if not self.enabled:
            return False
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        try:
            resp = requests.post(
                url,
                json={
                    "chat_id": self.chat_id,
                    "text": f"FATE QUANT\n{message}",
                    "disable_web_page_preview": True,
                },
                timeout=10,
            )
            if resp.status_code != 200:
                logger.warning(f"Telegram send failed: HTTP {resp.status_code}")
                return False
            return True
        except Exception as e:
            logger.warning(f"Telegram send error: {e}")
            return False
