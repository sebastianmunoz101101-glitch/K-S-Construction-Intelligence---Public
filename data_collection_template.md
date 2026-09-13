# Private Data Collection Template

This template shows the private fields required to calculate full margin and ROI metrics. Do not publish completed real rows in the public repo.

## Minimum private job table

| column | example |
|---|---|
| job_id | PRIVATE-2026-001 |
| date_quoted | 2026-09-12 |
| date_completed | 2026-09-24 |
| client_type | homeowner |
| scope | basement flooring |
| quoted_price | private_dollar_value |
| final_revenue | private_dollar_value |
| final_actual_cost | private_dollar_value |
| labor_hours | private_hour_value |
| subcontractor_cost | private_dollar_value |
| permit_cost | private_dollar_value |
| change_order_value | private_dollar_value |
| notes | sanitized internal note |

## Minimum private line-item table

| column | example |
|---|---|
| job_id | PRIVATE-2026-001 |
| item | vinyl_flooring_lvp |
| quantity | private_quantity_or_public_demo_quantity |
| unit | sqft |
| estimated_unit_cost | private_dollar_value |
| actual_unit_cost | private_dollar_value |
| vendor | supplier_category_or_sanitized_vendor |
| receipt_date | 2026-09-13 |
| notes | sanitized internal note |

## Public release rule

Public files should contain only synthetic demo rows, formulas, percent-based findings, and high-level business categories. Raw invoices, exact addresses, client names, and actual private job-cost dollars should stay private.
