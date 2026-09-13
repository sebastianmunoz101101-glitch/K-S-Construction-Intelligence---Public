import pandas as pd

from estimate import build_estimate, summarize_estimate


def test_build_estimate_basic():
    job = pd.DataFrame([
        {
            "job_id": "DEMO-TEST-001",
            "client": "Demo Client",
            "scope": "flooring",
            "item": "vinyl_flooring_lvp",
            "quantity": 100,
            "unit": "sqft",
            "data_status": "synthetic_public_demo_not_real_ks_dollars",
        }
    ])
    prices = pd.DataFrame([
        {
            "item": "vinyl_flooring_lvp",
            "unit": "sqft",
            "material_unit_cost": 2.0,
            "labor_hours_per_unit": 0.05,
            "default_waste_pct": 0.1,
        }
    ])

    result = build_estimate(job, prices, hourly_labor_rate=40, overhead_pct=0.1, profit_pct=0.2)

    assert len(result) == 1
    assert result.loc[0, "review_required"] is False or result.loc[0, "review_required"] == False
    assert round(float(result.loc[0, "material_cost"]), 2) == 220.00
    assert round(float(result.loc[0, "labor_cost"]), 2) == 200.00

    summary = summarize_estimate(result)
    assert summary.loc[0, "line_count"] == 1
    assert summary.loc[0, "data_status"] == "synthetic_public_demo_not_real_ks_dollars"
