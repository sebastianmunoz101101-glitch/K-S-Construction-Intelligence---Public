# K&S Construction Intelligence & Estimating System

Public, privacy-safe portfolio version of a construction estimating, quote-review, and KPI reporting workflow. The project demonstrates how messy construction records can be converted into structured, auditable analysis for supplier comparison, benchmark price variance, payment-structure tracking, change-scope tracking, reconciliation controls, profitability/ROI metric governance, and human-review quote controls.

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

## AI quote review assistant MVP

The project now includes a guardrailed quote-review assistant layer in `quote_review.py` and the Streamlit app. The assistant is intentionally conservative: it only uses structured estimate fields, flags missing inputs, separates blockers from warnings, and outputs a human-review note before any customer-facing quote is used.

The assistant checks for:

- Missing material-price assumptions
- Missing or invalid quantities
- Possible missing scope items by project type
- Possible duplicate line items
- Target-margin warnings
- Client-ready status for human review
- Markdown output for review documentation

This is the AI-engineering bridge in the project: it shows workflow design, structured inputs, validation, guardrails, evaluation cases, and human-in-the-loop controls instead of presenting an unverified chatbot as a finished estimator.

## Profitability, ROI, and business KPI model

The workflow defines calculation logic and required inputs for gross margin, net margin, ROI, quote-time reduction, CAC, CLV, retention, NPS, operating cash flow, sales conversion, and revenue per employee.

The key analyst control is that each KPI is only presented as a final business metric when the source row contains the required inputs. This mirrors real BI/reporting practice: supplier and benchmark metrics can be reported from quote evidence, while profitability and customer-performance metrics require revenue, actual cost, overhead, customer, quote-outcome, payment, and employee-hour fields.

## What this project proves

- Real-world data extraction and cleaning from messy construction records
- KPI definition and metric-governance discipline
- Supplier quote comparison and procurement analysis
- Benchmark price-positioning analysis
- Quote/payment structure modeling
- Guardrailed quote-review assistant logic
- Evaluation cases for expected assistant behavior
- Gross-margin, net-margin, ROI, and operating-KPI input validation
- Privacy-conscious portfolio publishing using synthetic public demo files
- Reproducible Python workflow suitable for junior data, operations, procurement, estimating, reporting, QA/business analyst, and AI-adjacent workflow roles

## Pipeline

```text
source records -> extracted fields -> standardized project/line-item tables -> estimate generation -> quote review assistant -> KPI calculations -> validation flags -> dashboard/review outputs
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
python quote_review.py --estimate sample_estimate.csv --output-json quote_review_output.json --output-md quote_review_output.md
python evaluate.py --history sample_historical_jobs.csv --output sample_evaluation.json
python eval_quote_review.py --cases sample_quote_review_cases.json --prices sample_material_prices.csv --output quote_review_eval_results.json
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

Built a privacy-safe Python/SQL construction intelligence workflow from a private K&S Construction source batch, adding estimate generation, KPI reporting, supplier savings analysis, benchmark price variance, quote-review guardrails, evaluation cases, and profitability/ROI metric governance; identified 21.9% quoted material savings, a comparable supplier quote priced ~2.3% lower, and strongest matched line items priced ~52.1% below benchmark midpoint.

## Validation notes

- Uses synthetic public demo files so raw business records remain private.
- Uses structured source records and manually verified extracted figures first for reliability.
- Uses input validation before reporting profitability, ROI, customer, cash-flow, and employee-productivity KPIs.
- Quote-review assistant outputs are decision-support outputs for human review before client use.
- Generated estimates are not final customer quotes until scope, measurements, market prices, and customer terms are confirmed.
- Supplier and benchmark comparisons should be timestamped so market pricing can be refreshed.
