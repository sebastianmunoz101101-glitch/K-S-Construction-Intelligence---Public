from __future__ import annotations

import pandas as pd

from estimate import build_estimate
from quote_review import review_estimate


def price_table() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"item": "drywall_1_2in", "unit": "sqft", "material_unit_cost": 0.65, "labor_hours_per_unit": 0.035, "default_waste_pct": 0.10},
            {"item": "insulation_r13", "unit": "sqft", "material_unit_cost": 0.92, "labor_hours_per_unit": 0.018, "default_waste_pct": 0.08},
            {"item": "vinyl_flooring_lvp", "unit": "sqft", "material_unit_cost": 2.75, "labor_hours_per_unit": 0.045, "default_waste_pct": 0.07},
            {"item": "baseboard_trim", "unit": "linear_ft", "material_unit_cost": 1.45, "labor_hours_per_unit": 0.030, "default_waste_pct": 0.10},
            {"item": "paint_wall", "unit": "sqft", "material_unit_cost": 0.38, "labor_hours_per_unit": 0.012, "default_waste_pct": 0.05},
        ]
    )


def test_complete_estimate_ready_for_human_review() -> None:
    jobs = pd.DataFrame(
        [
            {"job_id": "T-001", "client": "Demo Client", "scope": "basement_finish", "item": "drywall_1_2in", "quantity": 850, "unit": "sqft"},
            {"job_id": "T-001", "client": "Demo Client", "scope": "basement_finish", "item": "insulation_r13", "quantity": 600, "unit": "sqft"},
            {"job_id": "T-001", "client": "Demo Client", "scope": "basement_finish", "item": "vinyl_flooring_lvp", "quantity": 475, "unit": "sqft"},
            {"job_id": "T-001", "client": "Demo Client", "scope": "basement_finish", "item": "baseboard_trim", "quantity": 120, "unit": "linear_ft"},
            {"job_id": "T-001", "client": "Demo Client", "scope": "basement_finish", "item": "paint_wall", "quantity": 850, "unit": "sqft"},
        ]
    )
    review = review_estimate(build_estimate(jobs, price_table()))
    assert review["review_status"] == "ready_for_human_review"
    assert review["review_required_line_count"] == 0
    assert review["recommended_customer_quote"] > 0


def test_missing_price_blocks_final_quote() -> None:
    jobs = pd.DataFrame(
        [
            {"job_id": "T-002", "client": "Demo Client", "scope": "basement_finish", "item": "drywall_1_2in", "quantity": 500, "unit": "sqft"},
            {"job_id": "T-002", "client": "Demo Client", "scope": "basement_finish", "item": "custom_bar_buildout", "quantity": 1, "unit": "each"},
        ]
    )
    review = review_estimate(build_estimate(jobs, price_table()))
    assert review["review_status"] == "blocked_missing_inputs"
    assert any(blocker["issue"] == "missing_price" for blocker in review["blockers"])


def test_invalid_quantity_blocks_final_quote() -> None:
    jobs = pd.DataFrame(
        [
            {"job_id": "T-003", "client": "Demo Client", "scope": "flooring", "item": "vinyl_flooring_lvp", "quantity": 0, "unit": "sqft"},
            {"job_id": "T-003", "client": "Demo Client", "scope": "flooring", "item": "baseboard_trim", "quantity": 95, "unit": "linear_ft"},
        ]
    )
    review = review_estimate(build_estimate(jobs, price_table()))
    assert review["review_status"] == "blocked_missing_inputs"
    assert any(blocker["issue"] == "missing_or_invalid_quantity" for blocker in review["blockers"])
