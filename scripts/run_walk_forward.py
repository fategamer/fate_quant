"""
FATE QUANT — Phase D runner
"""

import sys
import os
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import TOTAL_CAPITAL_KES, ALLOWED_SYMBOLS


def main():
    print("=" * 60)
    print("FATE QUANT V1 — PHASE D")
    print("Out-of-sample + walk-forward testing")
    print("=" * 60)
    print(f"Capital: KES {TOTAL_CAPITAL_KES:,}")
    print(f"Universe: {ALLOWED_SYMBOLS}")
    print("Live trading: DISABLED")

    try:
        from backtesting.walk_forward import OutOfSampleTester, WalkForwardTester
    except Exception as e:
        print("Could not import walk-forward module:", e)
        traceback.print_exc()
        return

    oos_results = []
    wf_results = []
    try:
        print("\n### 1) 70/30 IN-SAMPLE vs OUT-OF-SAMPLE ###\n")
        oos_results = OutOfSampleTester().run_all()
        print("\n### 2) WALK-FORWARD ###\n")
        wf_results = WalkForwardTester().run_all()
    except Exception as e:
        print("Walk-forward run failed:", e)
        traceback.print_exc()

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
