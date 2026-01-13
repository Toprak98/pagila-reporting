import streamlit as st
import plotly.express as px
from db import get_connection, run_query

st.set_page_config(page_title="Pagila DWH Reporting", layout="wide")
st.title("📊 Pagila DWH Reporting (DMAR)")

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
    st.info("DB-Zugangsdaten links eingeben und **Connect** klicken.")
    st.stop()

try:
    conn = get_connection(host, database, user, password, port=int(port))
except Exception as e:
    st.error(f"Connection failed: {e}")
    st.stop()

# --- Quick connection test ---
try:
    total = run_query(conn, "SELECT COUNT(*) AS cnt FROM vw_rental_analysis;")["cnt"].iloc[0]
    st.success(f"Connected ✅  |  vw_rental_analysis records: {total}")
except Exception as e:
    st.error("Connected to DB, but cannot access vw_rental_analysis. "
             "Check view name/schema or permissions.\n\n"
             f"Error: {e}")
    conn.close()
    st.stop()

st.divider()

# --- Report 1: Rentals by Category ---
sql_cat = """
SELECT film_category,
       COUNT(*) AS total_rentals,
       SUM(rental_amount) AS total_revenue
FROM vw_rental_analysis
GROUP BY film_category
ORDER BY total_rentals DESC;
"""
df_cat = run_query(conn, sql_cat)
df_cat["total_revenue"] = df_cat["total_revenue"].fillna(0)

# --- Report 2: Trends over time (monthly) ---
sql_trend = """
SELECT year, month, month_name,
       COUNT(*) AS total_rentals,
       SUM(rental_amount) AS total_revenue
FROM vw_rental_analysis
GROUP BY year, month, month_name
ORDER BY year, month;
"""
df_trend = run_query(conn, sql_trend)
df_trend["total_revenue"] = df_trend["total_revenue"].fillna(0)
df_trend["period_label"] = df_trend["month_name"].astype(str) + " " + df_trend["year"].astype(str)
df_trend["sort_key"] = df_trend["year"] * 100 + df_trend["month"]

metric = st.radio("Metric", ["Rentals", "Revenue"], horizontal=True)
metric_key = "total_rentals" if metric == "Rentals" else "total_revenue"

left, right = st.columns(2)

with left:
    st.subheader("Report 1: By Film Category (Bar)")
    fig1 = px.bar(df_cat, x="film_category", y=metric_key, title=f"{metric} by Category")
    fig1.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig1, use_container_width=True)
    with st.expander("Show data"):
        st.dataframe(df_cat)

with right:
    st.subheader("Report 2: Trend Over Time (Line)")
    df_trend = df_trend.sort_values("sort_key")
    fig2 = px.line(df_trend, x="period_label", y=metric_key, markers=True, title=f"{metric} over Time")
    fig2.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig2, use_container_width=True)
    with st.expander("Show data"):
        st.dataframe(df_trend)

conn.close()
