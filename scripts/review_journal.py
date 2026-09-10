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
        return

    scans = opens = closes = 0
    pnls = []
    last_scans = []
    with open(PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ev = row.get("event")
            if ev == "SCAN":
                scans += 1
                last_scans.append(row)
            elif ev == "OPEN":
                opens += 1
            elif ev == "CLOSE":
                closes += 1
                try:
                    pnls.append(float(row.get("pnl") or 0))
                except ValueError:
                    pass

    print(f"Scans  : {scans}")
    print(f"Opens  : {opens}")
    print(f"Closes : {closes}")
    print(f"Net PnL: {sum(pnls):.2f}" if pnls else "Net PnL: n/a")
    if last_scans:
        print("Last scans:")
        for row in last_scans[-6:]:
            print(
                f"  {row.get('symbol')} score={row.get('score')} "
                f"price={row.get('price')} {row.get('reason')}"
            )
    print("Paper evidence only. Live trading locked.")


if __name__ == "__main__":
    main()
