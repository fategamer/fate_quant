"""
FATE QUANT — Alert bus
Phase E: log-only. Later can add Telegram.
"""

from loguru import logger


class AlertBus:
    def notify(self, message: str):
        logger.warning(f"ALERT | {message}")
        print(f"[ALERT] {message}")
