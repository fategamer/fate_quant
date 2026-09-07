"""
FATE QUANT — Gate runner
Runs tests + research + walk-forward in order.
Does not start live trading.
"""

import sys
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(title: str, args):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    result = subprocess.run(args, cwd=ROOT)
    if result.returncode != 0:
        print(f"GATE FAILED: {title}")
        return False
    return True


def main():
    print("FATE QUANT — GATE SEQUENCE")
    print("Live trading will not be enabled by this script.")

    steps = [
        ("UNIT TESTS", [sys.executable, "-m", "pytest", "tests/", "-q"]),
        ("RESEARCH / PORTFOLIO", [sys.executable, "scripts/run_research.py"]),
        ("OUT-OF-SAMPLE + WALK-FORWARD", [sys.executable, "scripts/run_walk_forward.py"]),
    ]

    failed = False
    for title, args in steps:
        ok = run(title, args)
        if not ok:
            failed = True
            break

    print("\n" + "=" * 60)
    if failed:
        print("OVERALL: FAIL — do not deploy")
    else:
        print("OVERALL: scripts completed. Review numbers before any next step.")
        print("Paper:   python scripts/run_paper.py")
        print("Testnet: python scripts/run_testnet.py")
        print("Live:    STILL LOCKED")
    print("=" * 60)


if __name__ == "__main__":
    main()
