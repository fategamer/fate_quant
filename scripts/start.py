"""
Simple start menu for FATE QUANT on a laptop.
"""

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(path):
    return subprocess.call([sys.executable, path], cwd=ROOT)


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

    mapping = {
        "1": ["-m", "pytest", "tests/", "-q"],
        "2": ["scripts/run_paper.py"],
        "3": ["scripts/run_research.py"],
        "4": ["scripts/run_walk_forward.py"],
        "5": ["scripts/setup_binance_testnet.py"],
        "6": ["scripts/run_testnet.py"],
    }
    if choice == "0":
        return
    if choice == "1":
        sys.exit(subprocess.call([sys.executable, "-m", "pytest", "tests/", "-q"], cwd=ROOT))
    if choice in mapping and choice != "1":
        sys.exit(run(os.path.join(ROOT, mapping[choice][0]) if mapping[choice][0].endswith(".py") else mapping[choice][0]))
    print("Unknown choice")


if __name__ == "__main__":
    main()
