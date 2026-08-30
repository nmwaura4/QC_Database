import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import date
from pathlib import Path
from database import get_connection
from config import APP_TITLE
from sidebar import show_sidebar

show_sidebar()
if not st.session_state.get("logged_in", False):
    st.switch_page("app.py")   # or whatever your main file is called
    st.stop()

st.title("📊 QC Dashboard")
st.caption("Quality Control Monitoring System")

st.divider()

# ---------------- LOAD DATA ----------------
conn = get_connection()

df = pd.read_sql_query(
    "SELECT * FROM users",
    conn
)

conn.close()

# ---------------- CHECK IF EMPTY ----------------
if df.empty:
    st.warning("No records found.")
    st.stop()

# ---------------- RECENT RECORDS ----------------
with st.expander("📂 View Recent Records"):

    recent = (
        df.sort_values(
            by="id",
            ascending=False
        )
        .head(5)
    )

    st.dataframe(
        recent,
        width="stretch"
    )

st.divider()

# ---------------- WEEKLY SUMMARY ----------------
st.subheader("📈 Weekly Average Counts by Product")

# Show the volume filter only if the database has a volume column
filtered_df = df

if "volume" in df.columns:

    volume_options = ["All"] + sorted(
        df["volume"].dropna().unique().tolist()
    )

    selected_volume = st.selectbox(
        "Package Volume",
        volume_options
    )

    if selected_volume != "All":
        filtered_df = df[
            df["volume"] == selected_volume
        ]

weekly_table = (
    filtered_df.pivot_table(
        index=["week", "product"],
        columns="market",
        values=[
            "initial_average_counts",
            "final_counts"
        ],
        aggfunc="mean"
    )
    .round(2)
)

st.dataframe(
    weekly_table,
    width="stretch"
)

# ---------------- EXCEL EXPORT ----------------
st.subheader("📥 Download Excel Report")

export_df = filtered_df.copy()

if "date" in export_df.columns:
    export_df["date"] = pd.to_datetime(export_df["date"], errors="coerce")
    export_df["week_label"] = (
        export_df["date"].dt.isocalendar().year.astype(str)
        + "-W"
        + export_df["date"].dt.isocalendar().week.astype(str).str.zfill(2)
    )
    export_df["month_label"] = export_df["date"].dt.to_period("M").astype(str)
    export_df["year_label"] = export_df["date"].dt.year.astype(str)

    period_filter = st.selectbox(
        "Export time filter",
        ["All time", "Week", "Month", "Year"],
        index=0,
    )

    selected_period = "All"

    if period_filter == "Week":
        week_options = ["All"] + sorted(
            export_df["week_label"].dropna().unique().tolist()
        )
        selected_period = st.selectbox("Select week", week_options)
        if selected_period != "All":
            export_df = export_df[export_df["week_label"] == selected_period]

    elif period_filter == "Month":
        month_options = ["All"] + sorted(
            export_df["month_label"].dropna().unique().tolist()
        )
        selected_period = st.selectbox("Select month", month_options)
        if selected_period != "All":
            export_df = export_df[export_df["month_label"] == selected_period]

    elif period_filter == "Year":
        year_options = ["All"] + sorted(
            export_df["year_label"].dropna().unique().tolist()
        )
        selected_period = st.selectbox("Select year", year_options)
        if selected_period != "All":
            export_df = export_df[export_df["year_label"] == selected_period]

    export_df = export_df.drop(columns=[col for col in ["week_label", "month_label", "year_label"] if col in export_df.columns], errors="ignore")

export_buffer = BytesIO()


def create_excel_report(output, data_frame):
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        data_frame.to_excel(writer, sheet_name="Filtered Records", index=False)
        weekly_table.to_excel(writer, sheet_name="Weekly Summary")

        overview = pd.DataFrame({
            "Metric": [
                "Total records",
                "Records in export",
                "Average initial counts",
                "Average final counts",
            ],
            "Value": [
                len(df),
                len(data_frame),
                round(data_frame["initial_average_counts"].mean(), 2) if "initial_average_counts" in data_frame.columns else 0,
                round(data_frame["final_counts"].mean(), 2) if "final_counts" in data_frame.columns else 0,
            ],
        })
        overview.to_excel(writer, sheet_name="Overview", index=False)


# Keep a current master workbook on the server for future downloads.
export_folder = Path("exports")
export_folder.mkdir(exist_ok=True)
master_export = export_folder / "QC_Dashboard.xlsx"
create_excel_report(master_export, export_df)
create_excel_report(export_buffer, export_df)

export_buffer.seek(0)
st.download_button(
    label="Download Excel report",
    data=export_buffer.getvalue(),
    file_name=f"QC_Dashboard_{date.today().isoformat()}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
)

st.divider()
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
