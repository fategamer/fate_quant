"""
FATE QUANT — Alert bus
Always logs. Telegram is optional.
"""

from loguru import logger
from alerts.telegram import TelegramSender


class AlertBus:
    def __init__(self):
        self.telegram = TelegramSender()

    def notify(self, message: str):
        logger.warning(f"ALERT | {message}")
        print(f"[ALERT] {message}")
        self.telegram.send(message)
