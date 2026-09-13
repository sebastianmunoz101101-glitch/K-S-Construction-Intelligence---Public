# K&S Construction Intelligence & Estimating System

Public, privacy-safe portfolio version of a construction estimating and KPI reporting workflow. The project demonstrates how messy construction records can be converted into structured, auditable analysis for supplier comparison, benchmark price variance, payment-structure tracking, change-scope tracking, reconciliation controls, and profitability/ROI metric governance.

## Public data privacy

This repository does **not** include raw source images, invoices, contracts, addresses, phone numbers, emails, client names, exact job totals, or actual K&S job-cost dollar records. Public CSV and JSON files are synthetic demo rows used only to show that the code runs. Business findings are reported as percentages, KPI categories, formulas, and validation logic rather than private source records.

## Source-backed KPI findings, reported safely

| KPI family | Public-safe finding | Business use |
|---|---:|---|
| Supplier quote savings | 21.9% quoted material savings on a supplier estimate | Procurement / vendor-cost analysis |
| Supplier comparison | Comparable supplier quote was approximately 2.3% lower than another supplier total | Vendor comparison |
| Benchmark price variance | Strongest matched line items were approximately 52.1% below a local benchmark midpoint | Market price-positioning analysis |
| Additional-item share | Itemized additional/change-scope items represented approximately 9.5% of a matching invoice total | Add-on scope tracking |
| Payment structure | Source records included staged payment models, including equal-stage and 50% / 25% / 25% structures | Cash-flow and payment-stage modeling |
| Reconciliation controls | Checkable source totals were routed through validation logic | Data-quality and auditability |

## Profitability, ROI, and business KPI model

The workflow defines calculation logic and required inputs for gross margin, net margin, ROI, quote-time reduction, CAC, CLV, retention, NPS, operating cash flow, sales conversion, and revenue per employee.

The key analyst control is that each KPI is only presented as a final business metric when the source row contains the required inputs. This mirrors real BI/reporting practice: supplier and benchmark metrics can be reported from quote evidence, while profitability and customer-performance metrics require revenue, actual cost, overhead, customer, quote-outcome, payment, and employee-hour fields.

## What this project proves

- Real-world data extraction and cleaning from messy construction records
- KPI definition and metric-governance discipline
- Supplier quote comparison and procurement analysis
- Benchmark price-positioning analysis
- Quote/payment structure modeling
- Gross-margin, net-margin, ROI, and operating-KPI input validation
- Privacy-conscious portfolio publishing using synthetic public demo files
- Reproducible Python workflow suitable for junior data, operations, procurement, estimating, and reporting roles

## Pipeline

```text
source records -> extracted fields -> standardized project/line-item tables -> KPI calculations -> validation flags -> resume/dashboard outputs
```

## Quick start

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate

pip install -r requirements.txt
python estimate.py --job sample_job_request.csv --prices sample_material_prices.csv --output sample_estimate.csv
python evaluate.py --history sample_historical_jobs.csv --output sample_evaluation.json
```

Optional UI:

```bash
streamlit run app.py
```

## Main metrics

- Supplier quote savings: `(subtotal - quoted_total) / subtotal`
- Supplier price variance: `(higher_supplier_total - lower_supplier_total) / higher_supplier_total`
- Benchmark price variance: `(benchmark_midpoint - source_price) / benchmark_midpoint`
- Additional-item share: `additional_item_total / invoice_total`
- Gross margin: `(final_revenue - actual_direct_cost) / final_revenue`
- Net margin: `(final_revenue - direct_costs - overhead) / final_revenue`
- ROI: `(verified_benefit - system_cost) / system_cost`
- Quote-time reduction: `(manual_quote_time - system_quote_time) / manual_quote_time`
- Sales conversion rate: `accepted_quotes / decided_quotes`
- Revenue per employee: `revenue / average_employee_count`
- Reconciliation status: checks whether source totals match computed totals

## Recommended resume bullet

Built a Python/SQL construction intelligence workflow from a private K&S Construction source batch, creating KPI reporting for supplier savings, benchmark price variance, payment structure, additional-item/change-scope tracking, reconciliation controls, and profitability/ROI metric governance; identified 21.9% quoted material savings, a comparable supplier quote priced ~2.3% lower, and strongest matched line items priced ~52.1% below benchmark midpoint.

## Validation notes

- Uses synthetic public demo files so raw business records remain private.
- Uses structured source records and manually verified extracted figures first for reliability.
- Uses input validation before reporting profitability, ROI, customer, cash-flow, and employee-productivity KPIs.
- Generated estimates are decision-support outputs for human review before client use.
- Supplier and benchmark comparisons should be timestamped so market pricing can be refreshed.
