"""
Simple start menu for FATE QUANT on a laptop.
"""

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_script(rel_path: str):
    return subprocess.call([sys.executable, os.path.join(ROOT, rel_path)], cwd=ROOT)


def main():
    print("=" * 50)
    print("FATE QUANT — START")
    print("Live trading is locked")
    print("=" * 50)
    print("1) Run tests")
    print("2) Paper trading (no real money)")
    print("3) Research backtest")
    print("4) Walk-forward / out-of-sample")
    print("5) Setup Binance TESTNET keys")
    print("6) Run Binance TESTNET")
    print("0) Exit")
    choice = input("Choose: ").strip()

    if choice == "0":
        return
    if choice == "1":
        sys.exit(subprocess.call([sys.executable, "-m", "pytest", "tests/", "-q"], cwd=ROOT))
    paths = {
        "2": "scripts/run_paper.py",
        "3": "scripts/run_research.py",
        "4": "scripts/run_walk_forward.py",
        "5": "scripts/setup_binance_testnet.py",
        "6": "scripts/run_testnet.py",
    }
    if choice in paths:
        sys.exit(run_script(paths[choice]))
    print("Unknown choice")


if __name__ == "__main__":
    main()
