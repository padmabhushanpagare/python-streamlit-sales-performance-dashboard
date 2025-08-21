# app.py
# Sales Performance Dashboard – Streamlit
# ---------------------------------------
# Features
# - Load cleaned CSV (auto) or upload raw CSV
# - Robust column handling for this dataset: YEAR, MONTH, SUPPLIER, ITEM CODE, ITEM DESCRIPTION, ITEM TYPE,
#   RETAIL SALES, RETAIL TRANSFERS, WAREHOUSE SALES
# - Sidebar filters (Year, Supplier, Item Type)
# - KPIs: Total Retail Sales, Retail Transfers, Warehouse Sales, Avg Monthly Sales
# - Interactive charts: Monthly trend, Top Suppliers, Top Items, Retail vs Warehouse over time
# - Download filtered data & KPI summary
# - Lightweight libs: pandas, numpy, altair, streamlit

import io
from typing import Dict

import numpy as np
import pandas as pd
import streamlit as st
import altair as alt

st.set_page_config(page_title="Sales Performance Dashboard", layout="wide")
st.title("📊 Sales Performance Dashboard")

# -----------------------------
# Helpers
# -----------------------------
REQUIRED_COLS = [
    "YEAR", "MONTH", "SUPPLIER", "ITEM CODE", "ITEM DESCRIPTION", "ITEM TYPE",
    "RETAIL SALES", "RETAIL TRANSFERS", "WAREHOUSE SALES"
]

RENAME_MAP = {
    "ITEM CODE": "ITEM_CODE",
    "ITEM DESCRIPTION": "ITEM_DESCRIPTION",
    "ITEM TYPE": "ITEM_TYPE",
    "RETAIL SALES": "RETAIL_SALES",
    "RETAIL TRANSFERS": "RETAIL_TRANSFERS",
    "WAREHOUSE SALES": "WAREHOUSE_SALES",
}


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    cols = [c.strip().upper() for c in df.columns]
    df.columns = cols
    # Only rename those we know
    for old, new in RENAME_MAP.items():
        if old in df.columns:
            df.rename(columns={old: new}, inplace=True)
    return df


@st.cache_data(show_spinner=False)
def load_default_data() -> pd.DataFrame:
    try:
        df = pd.read_csv("cleaned_warehouse_and_retail_sales.csv")
    except Exception:
        df = pd.read_csv("E:\projects for core statistics in data science\sales_performance_dashboard\Warehouse_and_Retail_Sales.csv")
    df = standardize_columns(df)
    return df


@st.cache_data(show_spinner=False)
def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    df = standardize_columns(df.copy())

    # Validate presence of required columns (allow subset but must have sales + year/month)
    missing = [c for c in ["YEAR", "MONTH", "RETAIL SALES", "RETAIL_SALES", "WAREHOUSE SALES", "WAREHOUSE_SALES"] if c not in df.columns]
    # After standardize, either with spaces or underscores may exist; handle both

    # Ensure numeric types for sales
    for col in ["RETAIL_SALES", "RETAIL TRANSFERS", "RETAIL_TRANSFERS", "WAREHOUSE_SALES", "RETAIL SALES", "RETAIL TRANSFERS", "WAREHOUSE SALES"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Coalesce dual-named columns into underscore versions
    if "RETAIL SALES" in df.columns and "RETAIL_SALES" not in df.columns:
        df.rename(columns={"RETAIL SALES": "RETAIL_SALES"}, inplace=True)
    if "RETAIL TRANSFERS" in df.columns and "RETAIL_TRANSFERS" not in df.columns:
        df.rename(columns={"RETAIL TRANSFERS": "RETAIL_TRANSFERS"}, inplace=True)
    if "WAREHOUSE SALES" in df.columns and "WAREHOUSE_SALES" not in df.columns:
        df.rename(columns={"WAREHOUSE SALES": "WAREHOUSE_SALES"}, inplace=True)

    # Category-like cols
    for c in ["SUPPLIER", "ITEM_CODE", "ITEM_DESCRIPTION", "ITEM_TYPE"]:
        if c in df.columns:
            df[c] = df[c].astype("category")

    # Fill missing sales with 0 (safer for aggregation)
    for c in ["RETAIL_SALES", "RETAIL_TRANSFERS", "WAREHOUSE_SALES"]:
        if c in df.columns:
            df[c] = df[c].fillna(0)

    # Month-Year label for plotting
    if "YEAR" in df.columns and "MONTH" in df.columns:
        # Keep MONTH as int 1-12 if possible
        df["YEAR"] = pd.to_numeric(df["YEAR"], errors="coerce").astype("Int64")
        df["MONTH"] = pd.to_numeric(df["MONTH"], errors="coerce").astype("Int64")
        # Construct a label like 2023-01
        df = df.dropna(subset=["YEAR", "MONTH"]).copy()
        df["MONTH_YEAR"] = pd.to_datetime(
            dict(year=df["YEAR"].astype(int), month=df["MONTH"].astype(int), day=1)
        ).dt.to_period("M").astype(str)

    return df


def kpi_block(filtered: pd.DataFrame) -> Dict[str, float]:
    kpis = {}
    kpis["Total Retail Sales"] = float(filtered.get("RETAIL_SALES", pd.Series([0])).sum())
    kpis["Total Retail Transfers"] = float(filtered.get("RETAIL_TRANSFERS", pd.Series([0])).sum())
    kpis["Total Warehouse Sales"] = float(filtered.get("WAREHOUSE_SALES", pd.Series([0])).sum())
    # Avg monthly retail sales
    if "MONTH_YEAR" in filtered.columns:
        monthly = filtered.groupby("MONTH_YEAR")["RETAIL_SALES"].sum()
        kpis["Avg Monthly Retail Sales"] = float(monthly.mean()) if len(monthly) else 0.0
    else:
        kpis["Avg Monthly Retail Sales"] = 0.0
    return kpis


# -----------------------------
# Data input
# -----------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    use_upload = st.toggle("Upload my own CSV", value=False)

if use_upload:
    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded is not None:
        raw = pd.read_csv(uploaded)
    else:
        st.info("Upload a CSV to proceed or turn off upload to use local data.")
        st.stop()
else:
    raw = load_default_data()

# Preprocess
_df = preprocess(raw)

# -----------------------------
# Sidebar filters
# -----------------------------
with st.sidebar:
    st.header("🔎 Filters")
    # Year filter
    if "YEAR" in _df.columns:
        years = sorted([int(x) for x in _df["YEAR"].dropna().unique()])
        year_sel = st.multiselect("Year", options=years, default=years)
    else:
        year_sel = []

    # Supplier filter
    if "SUPPLIER" in _df.columns:
        suppliers = sorted(list(_df["SUPPLIER"].astype(str).unique()))
        supplier_sel = st.multiselect("Supplier", options=suppliers, default=suppliers[:10])
    else:
        supplier_sel = []

    # Item Type filter
    if "ITEM_TYPE" in _df.columns:
        types = sorted(list(_df["ITEM_TYPE"].astype(str).unique()))
        type_sel = st.multiselect("Item Type", options=types, default=types)
    else:
        type_sel = []

# Apply filters
filtered = _df.copy()
if year_sel:
    filtered = filtered[filtered["YEAR"].isin(year_sel)]
if supplier_sel and "SUPPLIER" in filtered.columns:
    filtered = filtered[filtered["SUPPLIER"].astype(str).isin(supplier_sel)]
if type_sel and "ITEM_TYPE" in filtered.columns:
    filtered = filtered[filtered["ITEM_TYPE"].astype(str).isin(type_sel)]

# -----------------------------
# KPIs
# -----------------------------
kpis = kpi_block(filtered)

kpi_cols = st.columns(4)
for i, (k, v) in enumerate(kpis.items()):
    with kpi_cols[i % 4]:
        st.metric(label=k, value=f"{v:,.0f}")

st.markdown("---")

# -----------------------------
# Charts
# -----------------------------
# Ensure datetime conversion
if "MONTH_YEAR" in filtered.columns:
    filtered["MONTH_YEAR"] = pd.to_datetime(filtered["MONTH_YEAR"])

# 1) Monthly Retail Sales Trend
if "MONTH_YEAR" in filtered.columns:
    monthly_sales = filtered.groupby("MONTH_YEAR", as_index=False)["RETAIL_SALES"].sum()
    chart1 = (
        alt.Chart(monthly_sales)
        .mark_line(point=True)
        .encode(
            x=alt.X("MONTH_YEAR:T", title="Month-Year"),
            y=alt.Y("RETAIL_SALES:Q", title="Retail Sales"),
            tooltip=["MONTH_YEAR", alt.Tooltip("RETAIL_SALES:Q", format=",")]
        )
        .properties(height=320)
        .interactive()
    )
    st.subheader("📈 Monthly Retail Sales Trend")
    st.altair_chart(chart1, use_container_width=True)
else:
    st.warning("MONTH_YEAR column not available for trend chart.")

# 2) Top 10 Suppliers by Retail Sales
if "SUPPLIER" in filtered.columns:
    top_suppliers = (
        filtered.groupby("SUPPLIER", as_index=False)["RETAIL_SALES"]
        .sum()
        .nlargest(10, "RETAIL_SALES"))
    chart2 = (
        alt.Chart(top_suppliers)
        .mark_bar()
        .encode(
            y=alt.Y("SUPPLIER:N", sort='-x', title="Supplier", axis=alt.Axis(labelLimit=200)),
            x=alt.X("RETAIL_SALES:Q", title="Retail Sales"),
            tooltip=["SUPPLIER", alt.Tooltip("RETAIL_SALES:Q", format=",")]
        )
        .properties(height=360)
    )
    st.subheader("🏆 Top 10 Suppliers by Retail Sales")
    st.altair_chart(chart2, use_container_width=True)

# 3) Top 10 Items by Retail Sales
filtered["ITEM_DESCRIPTION"] = filtered["ITEM_DESCRIPTION"].astype(str)
if "ITEM_DESCRIPTION" in filtered.columns:
    top_items = (
        filtered.groupby("ITEM_DESCRIPTION", as_index=False)["RETAIL_SALES"]
        .sum()
        .nlargest(10, "RETAIL_SALES")
    )
    chart3 = (
        alt.Chart(top_items)
        .mark_bar()
        .encode(
            y=alt.Y("ITEM_DESCRIPTION:N", sort='-x', title="Item", axis=alt.Axis(labelLimit=200)),
            x=alt.X("RETAIL_SALES:Q", title="Retail Sales"),
            tooltip=["ITEM_DESCRIPTION", alt.Tooltip("RETAIL_SALES:Q", format=",")]
        )
        .properties(height=360)
    )
    st.subheader("📦 Top 10 Items by Retail Sales")
    st.altair_chart(chart3, use_container_width=True)

# 4) Retail vs Warehouse Sales Over Time
if "MONTH_YEAR" in filtered.columns:
    compare = (
        filtered.groupby("MONTH_YEAR", as_index=False)[["RETAIL_SALES", "WAREHOUSE_SALES"]]
        .sum()
        .sort_values("MONTH_YEAR")
    )
    compare_melt = compare.melt("MONTH_YEAR", var_name="Channel", value_name="Sales")
    chart4 = (
        alt.Chart(compare_melt)
        .mark_line(point=True)
        .encode(
            x=alt.X("MONTH_YEAR:T", title="Month-Year"),
            y=alt.Y("Sales:Q", title="Sales"),
            color="Channel:N",
            tooltip=["MONTH_YEAR", "Channel", alt.Tooltip("Sales:Q", format=",")]
        )
        .properties(height=320)
        .interactive()
    )
    st.subheader("📊 Retail vs Warehouse Sales Over Time")
    st.altair_chart(chart4, use_container_width=True)

st.markdown("---")


# -----------------------------
# Data preview and downloads
# -----------------------------
st.subheader("Filtered Data Preview")
st.dataframe(filtered.head(1000))

# Download filtered data
csv_buf = io.StringIO()
filtered.to_csv(csv_buf, index=False)
st.download_button(
    label="⬇️ Download Filtered CSV",
    data=csv_buf.getvalue(),
    file_name="filtered_sales.csv",
    mime="text/csv",
)

# KPI report download
kpi_text = "\n".join([f"{k}: {v:,.0f}" for k, v in kpis.items()])
st.download_button(
    label="⬇️ Download KPI Summary (TXT)",
    data=kpi_text,
    file_name="kpi_summary.txt",
    mime="text/plain",
)

st.caption("Built with Streamlit • Lightweight • Ready for portfolio demos")
