"""
Summarize paper journal if it exists.
"""

import csv
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "database", "journal", "paper_trades.csv")


def main():
    print("FATE QUANT — journal review")
    if not os.path.exists(PATH):
        print("No paper journal yet.")
        print("Run: python scripts/run_paper.py")
        return

    opens = closes = 0
    pnls = []
    with open(PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("event") == "OPEN":
                opens += 1
            elif row.get("event") == "CLOSE":
                closes += 1
                try:
                    pnls.append(float(row.get("pnl") or 0))
                except ValueError:
                    pass

    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p <= 0]
    print(f"Opens  : {opens}")
    print(f"Closes : {closes}")
    print(f"Net PnL: {sum(pnls):.2f}" if pnls else "Net PnL: n/a")
    if pnls:
        print(f"Wins   : {len(wins)}")
        print(f"Losses : {len(losses)}")
    print("This is paper evidence only. Not live results.")


if __name__ == "__main__":
    main()
