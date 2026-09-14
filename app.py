from __future__ import annotations

import pandas as pd
import streamlit as st
from estimate import build_estimate, summarize_estimate
from quote_review import review_estimate, review_to_markdown

st.set_page_config(page_title="K&S Estimate Generator", layout="wide")
st.title("K&S Construction Estimate Generator — Public Demo")
st.write(
    "Upload a structured job CSV and a material price CSV to generate a traceable estimate and guardrailed quote review. "
    "The public demo uses synthetic rows only; private client records and actual job-cost dollars are not published."
)

job_file = st.file_uploader("Job request CSV", type=["csv"])
price_file = st.file_uploader("Material prices CSV", type=["csv"])
hourly_labor_rate = st.number_input("Hourly labor rate", min_value=0.0, value=35.0, step=1.0)
overhead_pct = st.number_input("Overhead percentage", min_value=0.0, max_value=1.0, value=0.12, step=0.01)
profit_pct = st.number_input("Target profit percentage", min_value=0.0, max_value=0.9, value=0.25, step=0.01)
review_target_margin = st.number_input(
    "Review target margin percentage",
    min_value=0.0,
    max_value=0.9,
    value=profit_pct,
    step=0.01,
)

if job_file and price_file:
    estimate = build_estimate(
        pd.read_csv(job_file),
        pd.read_csv(price_file),
        hourly_labor_rate,
        overhead_pct,
        profit_pct,
    )
    summary = summarize_estimate(estimate)
    review = review_estimate(estimate, target_margin_pct=review_target_margin)
    review_markdown = review_to_markdown(review)

    st.subheader("Estimate Summary")
    st.dataframe(summary, use_container_width=True)

    st.subheader("Quote Review Assistant")
    st.metric("Review status", review["review_status"])
    st.write(review["client_ready_note"])

    col1, col2, col3 = st.columns(3)
    col1.metric("Review-required lines", review["review_required_line_count"])
    col2.metric("Recommended quote", f"${review['recommended_customer_quote']:,.2f}")
    if review["expected_margin_pct"] is not None:
        col3.metric("Expected margin", f"{review['expected_margin_pct']:.2%}")
    else:
        col3.metric("Expected margin", "Not available")

    if review["blockers"]:
        st.error("Blockers must be resolved before sending a final quote.")
        st.dataframe(pd.DataFrame(review["blockers"]), use_container_width=True)
    else:
        st.success("No blocker issues found from the provided fields.")

    if review["warnings"]:
        st.warning("Warnings should be checked during human review.")
        st.dataframe(pd.DataFrame(review["warnings"]), use_container_width=True)

    st.subheader("Line Items")
    st.dataframe(estimate, use_container_width=True)

    st.download_button(
        "Download estimate CSV",
        estimate.to_csv(index=False).encode("utf-8"),
        "estimate.csv",
        "text/csv",
    )
    st.download_button(
        "Download quote review Markdown",
        review_markdown.encode("utf-8"),
        "quote_review_output.md",
        "text/markdown",
    )
else:
    st.info("Upload both CSV files to run the estimator and quote review assistant.")
