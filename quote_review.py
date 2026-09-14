from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

REQUIRED_ESTIMATE_COLUMNS = {
    "job_id",
    "scope",
    "item",
    "quantity",
    "unit",
    "review_required",
    "missing_price_flag",
    "missing_quantity_flag",
    "material_cost",
    "labor_hours",
    "labor_cost",
    "line_cost_before_markup",
    "recommended_quote",
}

EXPECTED_SCOPE_ITEMS = {
    "basement_finish": {
        "drywall_1_2in",
        "insulation_r13",
        "vinyl_flooring_lvp",
        "baseboard_trim",
        "paint_wall",
    },
    "flooring": {"vinyl_flooring_lvp", "baseboard_trim"},
    "drywall": {"drywall_1_2in", "paint_wall"},
    "insulation": {"insulation_r13"},
}


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if pd.isna(value):
        return False
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if pd.isna(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def validate_estimate_columns(df: pd.DataFrame) -> None:
    missing = REQUIRED_ESTIMATE_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Estimate is missing required columns: {sorted(missing)}")


def review_estimate(lines: pd.DataFrame, target_margin_pct: float = 0.25) -> dict[str, Any]:
    """Return a guardrailed quote review for a construction estimate.

    This is a deterministic review layer intended to imitate the controls an
    AI assistant should respect before producing a client-facing quote: it only
    uses provided estimate fields, flags missing inputs, and separates verified
    calculations from review notes. Public demo rows are synthetic.
    """
    validate_estimate_columns(lines)
    df = lines.copy()

    for col in [
        "quantity",
        "material_cost",
        "labor_hours",
        "labor_cost",
        "line_cost_before_markup",
        "recommended_quote",
    ]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["review_required"] = df["review_required"].apply(_to_bool)
    df["missing_price_flag"] = df["missing_price_flag"].apply(_to_bool)
    df["missing_quantity_flag"] = df["missing_quantity_flag"].apply(_to_bool)

    usable = ~df["review_required"]
    review_lines = df[df["review_required"]].copy()
    usable_lines = df[usable].copy()

    total_cost = float(usable_lines["line_cost_before_markup"].sum()) if len(usable_lines) else 0.0
    recommended_quote = float(usable_lines["recommended_quote"].sum()) if len(usable_lines) else 0.0
    expected_profit = recommended_quote - total_cost
    expected_margin = expected_profit / recommended_quote if recommended_quote else None

    findings: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    for _, row in review_lines.iterrows():
        item = row.get("item")
        if row.get("missing_price_flag"):
            blockers.append(
                {
                    "severity": "blocker",
                    "item": item,
                    "issue": "missing_price",
                    "recommended_action": "Add a current material price and labor-hour assumption before sending the quote.",
                }
            )
        if row.get("missing_quantity_flag"):
            blockers.append(
                {
                    "severity": "blocker",
                    "item": item,
                    "issue": "missing_or_invalid_quantity",
                    "recommended_action": "Confirm the quantity and unit from the job scope before pricing this line.",
                }
            )

    if expected_margin is not None and expected_margin < target_margin_pct:
        warnings.append(
            {
                "severity": "warning",
                "issue": "target_margin_not_met",
                "observed_margin_pct": round(expected_margin, 4),
                "target_margin_pct": target_margin_pct,
                "recommended_action": "Review labor rate, overhead, and markup before sending a customer-facing quote.",
            }
        )

    scope_value = str(df["scope"].iloc[0]) if len(df) else ""
    expected_items = EXPECTED_SCOPE_ITEMS.get(scope_value, set())
    present_items = set(df["item"].dropna().astype(str))
    missing_scope_items = sorted(expected_items - present_items)
    if missing_scope_items:
        warnings.append(
            {
                "severity": "warning",
                "issue": "possible_missing_scope_items",
                "missing_items": missing_scope_items,
                "recommended_action": "Confirm whether these common scope items are intentionally excluded or missing from the estimate.",
            }
        )

    duplicate_mask = df.duplicated(subset=["job_id", "scope", "item", "unit"], keep=False)
    if duplicate_mask.any():
        duplicate_items = sorted(set(df.loc[duplicate_mask, "item"].astype(str)))
        warnings.append(
            {
                "severity": "warning",
                "issue": "possible_duplicate_lines",
                "duplicate_items": duplicate_items,
                "recommended_action": "Verify whether duplicate line items represent separate rooms/areas or accidental double-counting.",
            }
        )

    for _, row in usable_lines.iterrows():
        line_quote = _safe_float(row.get("recommended_quote"))
        line_cost = _safe_float(row.get("line_cost_before_markup"))
        line_margin = (line_quote - line_cost) / line_quote if line_quote else None
        findings.append(
            {
                "item": row.get("item"),
                "quantity": _safe_float(row.get("quantity")),
                "unit": row.get("unit"),
                "line_cost_before_markup": round(line_cost, 2),
                "recommended_quote": round(line_quote, 2),
                "expected_margin_pct": round(line_margin, 4) if line_margin is not None else None,
            }
        )

    status = "ready_for_human_review"
    if blockers:
        status = "blocked_missing_inputs"
    elif warnings:
        status = "review_recommended"

    return {
        "data_status": "synthetic_public_demo_not_real_ks_dollars",
        "review_status": status,
        "job_id": df["job_id"].iloc[0] if len(df) else None,
        "scope": scope_value if scope_value else None,
        "line_count": int(len(df)),
        "priced_line_count": int(len(usable_lines)),
        "review_required_line_count": int(len(review_lines)),
        "estimated_cost_before_markup": round(total_cost, 2),
        "recommended_customer_quote": round(recommended_quote, 2),
        "expected_profit": round(expected_profit, 2),
        "expected_margin_pct": round(expected_margin, 4) if expected_margin is not None else None,
        "blockers": blockers,
        "warnings": warnings,
        "priced_line_findings": findings,
        "client_ready_note": build_client_ready_note(status, blockers, warnings),
    }


def build_client_ready_note(status: str, blockers: list[dict[str, Any]], warnings: list[dict[str, Any]]) -> str:
    if status == "blocked_missing_inputs":
        return (
            "Do not send as a final customer quote yet. Required price or quantity inputs are missing. "
            "Resolve blocker items, rerun the estimate, and then perform human review."
        )
    if status == "review_recommended":
        return (
            "Quote can move to human review, but warnings should be checked before sending. "
            "Confirm scope coverage, duplicates, margin targets, and assumptions."
        )
    return (
        "Quote is ready for human review based on the provided synthetic demo fields. "
        "A human estimator should still confirm scope, measurements, market prices, and customer terms."
    )


def review_to_markdown(review: dict[str, Any]) -> str:
    lines = [
        "# K&S AI Quote Review Assistant Output",
        "",
        f"**Review status:** {review['review_status']}",
        f"**Job ID:** {review.get('job_id')}",
        f"**Scope:** {review.get('scope')}",
        f"**Data status:** {review['data_status']}",
        "",
        "## Summary",
        f"- Line count: {review['line_count']}",
        f"- Priced line count: {review['priced_line_count']}",
        f"- Review-required lines: {review['review_required_line_count']}",
        f"- Estimated cost before markup: ${review['estimated_cost_before_markup']:,.2f}",
        f"- Recommended customer quote: ${review['recommended_customer_quote']:,.2f}",
        f"- Expected margin: {review['expected_margin_pct']:.2%}" if review.get("expected_margin_pct") is not None else "- Expected margin: not available",
        "",
        "## Client-ready control note",
        review["client_ready_note"],
        "",
        "## Blockers",
    ]

    if review["blockers"]:
        for blocker in review["blockers"]:
            lines.append(f"- {blocker['item']}: {blocker['issue']} — {blocker['recommended_action']}")
    else:
        lines.append("- None")

    lines.extend(["", "## Warnings"])
    if review["warnings"]:
        for warning in review["warnings"]:
            issue = warning.get("issue")
            action = warning.get("recommended_action")
            lines.append(f"- {issue}: {action}")
    else:
        lines.append("- None")

    lines.extend(["", "## Priced line findings"])
    for finding in review["priced_line_findings"]:
        lines.append(
            f"- {finding['item']}: {finding['quantity']} {finding['unit']} | "
            f"cost ${finding['line_cost_before_markup']:,.2f} | "
            f"quote ${finding['recommended_quote']:,.2f} | "
            f"margin {finding['expected_margin_pct']:.2%}"
        )

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--estimate", required=True, help="Path to generated estimate CSV")
    parser.add_argument("--output-json", default="quote_review_output.json")
    parser.add_argument("--output-md", default="quote_review_output.md")
    parser.add_argument("--target-margin-pct", type=float, default=0.25)
    args = parser.parse_args()

    review = review_estimate(pd.read_csv(args.estimate), target_margin_pct=args.target_margin_pct)
    Path(args.output_json).write_text(json.dumps(review, indent=2), encoding="utf-8")
    Path(args.output_md).write_text(review_to_markdown(review), encoding="utf-8")
    print(json.dumps(review, indent=2))


if __name__ == "__main__":
    main()
