import pandas as pd
import streamlit as st
import plotly.express as px
from db import get_connection, run_query

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(page_title="Pagila DWH Reporting", layout="wide")
st.title("Pagila DWH Reporting")

# --------------------------------------------------
# Sidebar: Database Connection
# --------------------------------------------------
st.sidebar.header("Database Connection")

host = st.sidebar.text_input("Host", value="localhost")
port = st.sidebar.number_input("Port", value=5432, step=1)
database = st.sidebar.text_input("Database", value="pagila_dwh")
user = st.sidebar.text_input("User", value="postgres")
password = st.sidebar.text_input("Password", type="password")

connect_btn = st.sidebar.button("Connect")

if "connected" not in st.session_state:
    st.session_state["connected"] = False

if connect_btn:
    st.session_state["connected"] = True

if not st.session_state["connected"]:
    st.info("Please enter database credentials on the left and click Connect.")
    st.stop()

# --------------------------------------------------
# Connect to database
# --------------------------------------------------
try:
    conn = get_connection(host, database, user, password, port=int(port))
except Exception as e:
    st.error(f"Connection failed: {e}")
    st.stop()

# Quick connection test
try:
    total = run_query(
        conn,
        "SELECT COUNT(*) AS cnt FROM vw_rental_analysis;"
    )["cnt"].iloc[0]
    st.success(f"Connected successfully | vw_rental_analysis records: {total}")
except Exception as e:
    st.error(
        "Connected to database, but vw_rental_analysis is not accessible.\n\n"
        f"Error: {e}"
    )
    conn.close()
    st.stop()

st.divider()

# --------------------------------------------------
# SQL Queries
# --------------------------------------------------
# Report 1: Rentals / Revenue by category
sql_category = """
SELECT
    film_category,
    COUNT(*) AS total_rentals,
    SUM(rental_amount) AS total_revenue
FROM vw_rental_analysis
GROUP BY film_category;
"""
df_cat = run_query(conn, sql_category)
df_cat["total_revenue"] = df_cat["total_revenue"].fillna(0)

# Report 2: Monthly trend
sql_trend = """
SELECT
    year,
    month,
    month_name,
    COUNT(*) AS total_rentals,
    SUM(rental_amount) AS total_revenue
FROM vw_rental_analysis
GROUP BY year, month, month_name
ORDER BY year, month;
"""
df_trend = run_query(conn, sql_trend)
df_trend["total_revenue"] = df_trend["total_revenue"].fillna(0)

# Create proper date column for x-axis
df_trend["period_date"] = pd.to_datetime(
    df_trend["year"].astype(str)
    + "-"
    + df_trend["month"].astype(str).str.zfill(2)
    + "-01"
)

# --------------------------------------------------
# Controls
# --------------------------------------------------
metric = st.radio("Metric", ["Rentals", "Revenue"], horizontal=True)
metric_key = "total_rentals" if metric == "Rentals" else "total_revenue"

# Sort data
df_cat_sorted = df_cat.sort_values(metric_key, ascending=False)
df_trend_sorted = df_trend.sort_values("period_date")

# --------------------------------------------------
# Charts (side by side, aligned)
# --------------------------------------------------
left, right = st.columns(2)

with left:
    st.subheader("Report 1: By Film Category\n(Bar)")
    fig1 = px.bar(
        df_cat_sorted,
        x="film_category",
        y=metric_key,
        title=f"{metric} by Category"
    )
    fig1.update_layout(
        xaxis_tickangle=-45,
        margin=dict(t=60, b=80)
    )
    st.plotly_chart(fig1, use_container_width=True)

with right:
    st.subheader("Report 2: Trend Over Time\n(Monthly)")
    fig2 = px.line(
        df_trend_sorted,
        x="period_date",
        y=metric_key,
        markers=True,
        title=f"{metric} over Time (Monthly)"
    )
    fig2.update_xaxes(
        tickformat="%b %Y",
        dtick="M3",
        tickangle=0
    )
    fig2.update_layout(
        margin=dict(t=60, b=80)  # aligns x-axis with left chart
    )
    st.plotly_chart(fig2, use_container_width=True)

# --------------------------------------------------
# Data Tables (aligned)
# --------------------------------------------------
st.divider()
st.subheader("Data Tables")

show_tables = st.checkbox("Show data tables", value=False)

if show_tables:
    t_left, t_right = st.columns(2)

    with t_left:
        st.caption("Report 1 data (by category)")
        st.dataframe(df_cat_sorted, use_container_width=True)

    with t_right:
        st.caption("Report 2 data (monthly trend)")
        st.dataframe(df_trend_sorted, use_container_width=True)

conn.close()
