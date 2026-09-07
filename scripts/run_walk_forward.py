"""
FATE QUANT — Phase D runner
Out-of-sample split + walk-forward tests.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import TOTAL_CAPITAL_KES, ALLOWED_SYMBOLS
from backtesting.walk_forward import OutOfSampleTester, WalkForwardTester


def main():
    print("=" * 60)
    print("FATE QUANT V1 — PHASE D")
    print("Out-of-sample + walk-forward testing")
    print("=" * 60)
    print(f"Capital: KES {TOTAL_CAPITAL_KES:,}")
    print(f"Universe: {ALLOWED_SYMBOLS}")
    print("Live trading: DISABLED")
    print()

    print("\n### 1) 70/30 IN-SAMPLE vs OUT-OF-SAMPLE ###\n")
    oos = OutOfSampleTester()
    oos_results = oos.run_all()

    print("\n### 2) WALK-FORWARD ###\n")
    wf = WalkForwardTester()
    wf_results = wf.run_all()

    print("\n" + "=" * 60)
    print("PHASE D GATE SUMMARY")
    print("=" * 60)

    fail_count = 0
    for r in oos_results:
        print(f"OOS {r.symbol}: {r.verdict}")
        if r.verdict.startswith("FAIL"):
            fail_count += 1
    for r in wf_results:
        print(f"WF  {r.symbol}: {r.verdict}")
        if r.verdict.startswith("FAIL"):
            fail_count += 1

    if fail_count > 0:
        print("\nGATE RESULT: DO NOT DEPLOY")
    elif not oos_results and not wf_results:
        print("\nGATE RESULT: INCONCLUSIVE — no usable results")
    else:
        print("\nGATE RESULT: REVIEW MANUALLY — only INTERESTING verdicts may proceed")


if __name__ == "__main__":
    main()
