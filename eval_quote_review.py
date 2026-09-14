from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from estimate import build_estimate
from quote_review import review_estimate


def run_cases(cases_path: str, prices_path: str) -> dict:
    cases = json.loads(Path(cases_path).read_text(encoding="utf-8"))
    prices = pd.read_csv(prices_path)
    results = []

    for case in cases:
        job_df = pd.DataFrame(case["job_rows"])
        lines = build_estimate(job_df, prices)
        review = review_estimate(lines)
        passed_status = review["review_status"] == case["expected_status"]
        passed_blockers = len(review["blockers"]) >= int(case["expected_min_blockers"])
        results.append(
            {
                "case_id": case["case_id"],
                "description": case["description"],
                "expected_status": case["expected_status"],
                "actual_status": review["review_status"],
                "blocker_count": len(review["blockers"]),
                "passed": bool(passed_status and passed_blockers),
            }
        )

    passed = sum(1 for row in results if row["passed"])
    return {
        "data_status": "synthetic_public_demo_not_real_ks_dollars",
        "cases_total": len(results),
        "cases_passed": passed,
        "pass_rate": round(passed / len(results), 4) if results else 0.0,
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default="sample_quote_review_cases.json")
    parser.add_argument("--prices", default="sample_material_prices.csv")
    parser.add_argument("--output", default="quote_review_eval_results.json")
    args = parser.parse_args()

    results = run_cases(args.cases, args.prices)
    Path(args.output).write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
