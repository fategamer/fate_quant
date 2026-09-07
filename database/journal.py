"""
FATE QUANT — Trade journal
Append-only CSV. No strategy logic here.
"""

import csv
import os
from datetime import datetime, timezone
from typing import Dict, Any

from config.settings import JOURNAL_DIR


class TradeJournal:
    def __init__(self, filename: str = "trades.csv"):
        os.makedirs(JOURNAL_DIR, exist_ok=True)
        self.path = os.path.join(JOURNAL_DIR, filename)
        if not os.path.exists(self.path):
            with open(self.path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp", "event", "symbol", "side", "quantity",
                    "price", "stop", "take_profit", "score", "pnl", "reason",
                ])

    def write(self, event: str, payload: Dict[str, Any]):
        row = [
            datetime.now(timezone.utc).isoformat(),
            event,
            payload.get("symbol", ""),
            payload.get("side", ""),
            payload.get("quantity", ""),
            payload.get("price", ""),
            payload.get("stop", ""),
            payload.get("take_profit", ""),
            payload.get("score", ""),
            payload.get("pnl", ""),
            payload.get("reason", ""),
        ]
        with open(self.path, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(row)
