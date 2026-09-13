from __future__ import annotations

import pandas as pd
import streamlit as st
from estimate import build_estimate, summarize_estimate

st.set_page_config(page_title="K&S Estimate Generator", layout="wide")
st.title("K&S Construction Estimate Generator — Public Demo")
st.write(
    "Upload a structured job CSV and a material price CSV to generate a traceable estimate. "
    "The public demo uses synthetic rows only; private client records and actual job-cost dollars are not published."
)

job_file = st.file_uploader("Job request CSV", type=["csv"])
price_file = st.file_uploader("Material prices CSV", type=["csv"])
hourly_labor_rate = st.number_input("Hourly labor rate", min_value=0.0, value=35.0, step=1.0)
overhead_pct = st.number_input("Overhead percentage", min_value=0.0, max_value=1.0, value=0.12, step=0.01)
profit_pct = st.number_input("Target profit percentage", min_value=0.0, max_value=0.9, value=0.25, step=0.01)

if job_file and price_file:
    estimate = build_estimate(
        pd.read_csv(job_file),
        pd.read_csv(price_file),
        hourly_labor_rate,
        overhead_pct,
        profit_pct,
    )
    st.subheader("Estimate Summary")
    st.dataframe(summarize_estimate(estimate), use_container_width=True)

    st.subheader("Line Items")
    st.dataframe(estimate, use_container_width=True)

    st.download_button(
        "Download estimate CSV",
        estimate.to_csv(index=False).encode("utf-8"),
        "estimate.csv",
        "text/csv",
    )
else:
    st.info("Upload both CSV files to run the estimator.")
