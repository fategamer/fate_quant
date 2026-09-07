"""
Daily session helper for the risk engine.
"""

from datetime import date, timezone, datetime
from risk.risk_engine import RiskEngine


class DailySession:
    def __init__(self, risk: RiskEngine):
        self.risk = risk
        self.current_day = datetime.now(timezone.utc).date()

    def roll(self):
        today = datetime.now(timezone.utc).date()
        if today != self.current_day:
            self.risk.reset_daily()
            self.current_day = today
            return True
        return False
