# Metrics Dictionary

This public metrics dictionary defines the KPI logic used by the project. Public demo rows are synthetic and do not expose actual K&S job-cost dollars.

## Supplier quote savings

`(supplier_subtotal - quoted_total) / supplier_subtotal`

Measures the percentage discount or quoted savings shown in a supplier estimate.

## Supplier price variance

`(higher_supplier_total - lower_supplier_total) / higher_supplier_total`

Compares two supplier totals for similar material scope.

## Benchmark price variance

`(benchmark_midpoint - source_price) / benchmark_midpoint`

Measures how far a source price is below or above a local benchmark midpoint.

## Additional-item / change-scope share

`additional_item_total / invoice_total`

Measures how much of an itemized invoice or scope packet comes from additional or changed work.

## Estimated cost

Predicted internal cost before markup.

## Quoted price

Customer-facing price after overhead and target profit.

## Actual cost

Final observed cost after materials, labor, subcontractors, permits, and other direct job expenses. In this public repo, sample actual-cost rows are synthetic.

## Estimate error

`estimated_cost - actual_cost`

Negative values mean the system underestimated cost.

## MAE

`mean(abs(estimated_cost - actual_cost))`

## MAPE

`mean(abs(estimated_cost - actual_cost) / actual_cost)`

## Gross margin

`(final_revenue - actual_cost) / final_revenue`

## Net margin

`(final_revenue - direct_costs - overhead) / final_revenue`

## ROI

`(verified_benefit - system_cost) / system_cost`

## Labor productivity

`completed_quantity / labor_hours`

## Sales conversion rate

`accepted_quotes / decided_quotes`

## Revenue per employee

`revenue / average_employee_count`
