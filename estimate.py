from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

REQUIRED_JOB_COLUMNS = {"job_id", "client", "scope", "item", "quantity", "unit"}
REQUIRED_PRICE_COLUMNS = {"item", "unit", "material_unit_cost", "labor_hours_per_unit", "default_waste_pct"}


def validate_columns(df: pd.DataFrame, required: set[str], name: str) -> None:
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{name} is missing required columns: {sorted(missing)}")


def build_estimate(
    job_df: pd.DataFrame,
    price_df: pd.DataFrame,
    hourly_labor_rate: float = 35.0,
    overhead_pct: float = 0.12,
    profit_pct: float = 0.25,
) -> pd.DataFrame:
    """Build a line-item construction estimate from structured job and price inputs.

    Public demo data is synthetic. The workflow is designed so private business
    records can be processed without publishing raw client or job-cost details.
    """
    validate_columns(job_df, REQUIRED_JOB_COLUMNS, "job_df")
    validate_columns(price_df, REQUIRED_PRICE_COLUMNS, "price_df")

    df = job_df.merge(price_df, on=["item", "unit"], how="left", indicator=True)
    df["missing_price_flag"] = df["_merge"].ne("both")

    for col in ["quantity", "material_unit_cost", "labor_hours_per_unit", "default_waste_pct"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["missing_quantity_flag"] = df["quantity"].isna() | (df["quantity"] <= 0)
    df["review_required"] = df["missing_price_flag"] | df["missing_quantity_flag"]
    usable = ~df["review_required"]

    for col in [
        "waste_adjusted_quantity",
        "material_cost",
        "labor_hours",
        "labor_cost",
        "line_cost_before_markup",
        "recommended_quote",
    ]:
        df[col] = None

    df.loc[usable, "waste_adjusted_quantity"] = df.loc[usable, "quantity"] * (
        1 + df.loc[usable, "default_waste_pct"]
    )
    df.loc[usable, "material_cost"] = (
        df.loc[usable, "waste_adjusted_quantity"] * df.loc[usable, "material_unit_cost"]
    )
    df.loc[usable, "labor_hours"] = df.loc[usable, "quantity"] * df.loc[usable, "labor_hours_per_unit"]
    df.loc[usable, "labor_cost"] = df.loc[usable, "labor_hours"] * hourly_labor_rate
    df.loc[usable, "line_cost_before_markup"] = df.loc[usable, "material_cost"] + df.loc[usable, "labor_cost"]
    df.loc[usable, "recommended_quote"] = df.loc[usable, "line_cost_before_markup"] * (1 + overhead_pct) / (
        1 - profit_pct
    )

    df["hourly_labor_rate"] = hourly_labor_rate
    df["overhead_pct"] = overhead_pct
    df["profit_pct"] = profit_pct
    df["data_status"] = df.get("data_status", "synthetic_public_demo_not_real_ks_dollars")

    return df.drop(columns=["_merge"])


def summarize_estimate(lines: pd.DataFrame) -> pd.DataFrame:
    usable = ~lines["review_required"]
    summary = {
        "job_id": lines["job_id"].iloc[0] if len(lines) else None,
        "client": lines["client"].iloc[0] if len(lines) else None,
        "scope": lines["scope"].iloc[0] if len(lines) else None,
        "line_count": int(len(lines)),
        "review_required_lines": int(lines["review_required"].sum()),
        "estimated_material_cost": round(float(lines.loc[usable, "material_cost"].sum()), 2),
        "estimated_labor_hours": round(float(lines.loc[usable, "labor_hours"].sum()), 2),
        "estimated_labor_cost": round(float(lines.loc[usable, "labor_cost"].sum()), 2),
        "estimated_cost_before_markup": round(float(lines.loc[usable, "line_cost_before_markup"].sum()), 2),
        "recommended_customer_quote": round(float(lines.loc[usable, "recommended_quote"].sum()), 2),
        "data_status": "synthetic_public_demo_not_real_ks_dollars",
    }
    return pd.DataFrame([summary])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", required=True)
    parser.add_argument("--prices", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--summary-output", default=None)
    parser.add_argument("--hourly-labor-rate", type=float, default=35.0)
    parser.add_argument("--overhead-pct", type=float, default=0.12)
    parser.add_argument("--profit-pct", type=float, default=0.25)
    args = parser.parse_args()

    lines = build_estimate(
        pd.read_csv(args.job),
        pd.read_csv(args.prices),
        args.hourly_labor_rate,
        args.overhead_pct,
        args.profit_pct,
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines.to_csv(out, index=False)

    summary_out = Path(args.summary_output) if args.summary_output else out.with_name(out.stem + "_summary.csv")
    summarize_estimate(lines).to_csv(summary_out, index=False)
    print(f"Wrote line estimate: {out}")
    print(f"Wrote summary: {summary_out}")


if __name__ == "__main__":
    main()
