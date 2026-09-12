import streamlit as st
import pandas as pd

from auth import login
from assets.style import load_css
from database import get_connection, initialize_database
from config import APP_TITLE
from sidebar import show_sidebar

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title=APP_TITLE,
    layout="wide"
)

show_sidebar()

# ---------------- INITIALIZE ----------------
load_css()
initialize_database()

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- LOGIN PAGE ----------------
if not st.session_state.logged_in:

    st.title("🔐 QC Database Login")
    st.caption("Please sign in to continue.")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        user = login(email, password)

        if user:
            st.session_state.logged_in = True
            st.session_state.role = user[0]
            st.rerun()

        else:
            st.error("Invalid email or password.")

    st.stop()


# ---------------- DASHBOARD LANDING PAGE ----------------

st.markdown("# Quality Control Overview")
st.caption("A quick view of production quality activity and the latest recorded checks.")

conn = get_connection()
records_df = pd.read_sql_query("SELECT * FROM users ORDER BY id DESC", conn)
conn.close()

if records_df.empty:
    latest_date = "No records yet"
    product_count = 0
    market_count = 0
else:
    dates = pd.to_datetime(records_df["date"], errors="coerce").dropna()
    latest_date = dates.max().strftime("%d %b %Y") if not dates.empty else "Unknown"
    product_count = records_df["product"].dropna().nunique()
    market_count = records_df["market"].dropna().nunique()

st.subheader("Key Metrics")
metric_columns = st.columns(4)
metrics = [
    ("Total QC Checks", f"{len(records_df):,}", "Number of recorded quality checks."),
    ("Unique Products", f"{product_count:,}", "Different products in the database."),
    ("Active Markets", f"{market_count:,}", "Different markets represented."),
    ("Most Recent Check", latest_date, "Date of the latest recorded check."),
]
for metric_column, (label, value, description) in zip(metric_columns, metrics):
    with metric_column:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-description">{description}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


st.divider()
action_columns = st.columns([1, 1, 2])
with action_columns[0]:
    if st.button("Add QC record", type="primary", use_container_width=True):
        st.switch_page("pages/Record.py")
with action_columns[1]:
    if st.button("Open full dashboard", use_container_width=True):
        st.switch_page("pages/Dashboard.py")

st.subheader("Recent activity")
if records_df.empty:
    st.info("No quality checks have been recorded yet. Add the first QC record to get started.")
else:
    recent_columns = [
        column for column in ["date", "product", "market", "customer_name", "final_counts", "remarks"]
        if column in records_df.columns
    ]
    recent_df = records_df[recent_columns].head(5).copy()
    recent_df = recent_df.rename(columns={
        "date": "Date",
        "product": "Product",
        "market": "Market",
        "customer_name": "Customer",
        "final_counts": "Final Counts",
        "remarks": "Remarks",
    })
    if "Date" in recent_df.columns:
        recent_df["Date"] = pd.to_datetime(
            recent_df["Date"], errors="coerce"
        ).dt.strftime("%d %b %Y")
    st.dataframe(recent_df, hide_index=True, use_container_width=True)

#----------------
#FOOTER
#----------------
st.markdown("""
<div style="
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background: #f8f9fa;
    color: #6c757d;
    text-align: center;
    padding: 12px 0;
    border-top: 1px solid #e9ecef;
    font-family: Arial, sans-serif;
    font-size: 13px;
    z-index: 999;
">
    © 2026 <strong>QC Database v1.0.0</strong> | All Rights Reserved
</div>
""", unsafe_allow_html=True)

    
