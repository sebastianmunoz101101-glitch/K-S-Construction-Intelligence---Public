from __future__ import annotations

import argparse
import json
from pathlib import Path
import pandas as pd

REQUIRED_HISTORY_COLUMNS = {
    "job_id",
    "estimated_cost",
    "quoted_price",
    "actual_cost",
    "final_revenue",
    "labor_hours",
    "change_order_value",
}


def safe_div(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    return numerator / denominator.replace(0, pd.NA)


def evaluate(history: pd.DataFrame) -> dict:
    """Evaluate estimate accuracy and job-cost KPIs from structured history rows.

    Public demo rows are synthetic. The same calculation pattern can be applied
    privately when real actual-cost and final-revenue records are available.
    """
    missing = REQUIRED_HISTORY_COLUMNS - set(history.columns)
    if missing:
        raise ValueError(f"Historical data missing required columns: {sorted(missing)}")

    df = history.copy()
    for col in REQUIRED_HISTORY_COLUMNS - {"job_id"}:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["estimated_cost", "actual_cost", "final_revenue"])
    if df.empty:
        raise ValueError("No complete historical rows available for evaluation.")

    df["estimate_error"] = df["estimated_cost"] - df["actual_cost"]
    df["absolute_error"] = df["estimate_error"].abs()
    df["absolute_pct_error"] = safe_div(df["absolute_error"], df["actual_cost"])
    df["gross_margin"] = safe_div(df["final_revenue"] - df["actual_cost"], df["final_revenue"])
    df["quote_to_actual_ratio"] = safe_div(df["quoted_price"], df["actual_cost"])
    df["change_order_share"] = safe_div(df["change_order_value"], df["final_revenue"])

    return {
        "data_status": "synthetic_public_demo_not_real_ks_dollars",
        "jobs_evaluated": int(len(df)),
        "mean_absolute_error_cost": round(float(df["absolute_error"].mean()), 2),
        "median_absolute_error_cost": round(float(df["absolute_error"].median()), 2),
        "mean_absolute_percentage_error": round(float(df["absolute_pct_error"].mean()), 4),
        "mean_gross_margin": round(float(df["gross_margin"].mean()), 4),
        "median_gross_margin": round(float(df["gross_margin"].median()), 4),
        "mean_quote_to_actual_ratio": round(float(df["quote_to_actual_ratio"].mean()), 4),
        "mean_change_order_share": round(float(df["change_order_share"].mean()), 4),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--history", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    metrics = evaluate(pd.read_csv(args.history))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
