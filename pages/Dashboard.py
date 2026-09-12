import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import date
from pathlib import Path
from database import delete_record, get_connection
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

if df.empty:
    st.warning("No records found.")
    st.stop()

with st.expander("📂 View Recent Records"):
    recent_filters = st.columns(3)

    with recent_filters[0]:
        recent_product_options = ["All"] + sorted(df["product"].dropna().astype(str).unique().tolist())
        recent_product = st.selectbox("Product", recent_product_options, key="recent_product")

    with recent_filters[1]:
        recent_market_options = ["All"] + sorted(df["market"].dropna().astype(str).unique().tolist())
        recent_market = st.selectbox("Market", recent_market_options, key="recent_market")

    with recent_filters[2]:
        recent_date_options = ["All"] + sorted(
            pd.to_datetime(df["date"], errors="coerce").dropna().dt.strftime("%Y-%m-%d").unique().tolist(),
            reverse=True,
        )
        recent_date = st.selectbox("Date", recent_date_options, key="recent_date")

    recent_df = df.copy()
    if recent_product != "All":
        recent_df = recent_df[recent_df["product"].astype(str) == recent_product]
    if recent_market != "All":
        recent_df = recent_df[recent_df["market"].astype(str) == recent_market]
    if recent_date != "All":
        recent_df = recent_df[
            pd.to_datetime(recent_df["date"], errors="coerce").dt.strftime("%Y-%m-%d") == recent_date
        ]

    recent = recent_df.sort_values(by="id", ascending=False).head(5).copy()
    recent["date"] = pd.to_datetime(recent["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    if recent.empty:
        st.info("No records match the selected filters.")
    else:
        st.dataframe(recent, width="stretch")

st.divider()
st.subheader("📈 Filter to delete")

filtered_df = df.copy()
filtered_df["date"] = pd.to_datetime(filtered_df["date"], errors="coerce")
iso_dates = filtered_df["date"].dt.isocalendar()
filtered_df["iso_year"] = iso_dates.year
filtered_df["week"] = iso_dates.week
filtered_df["week_label"] = (
    filtered_df["iso_year"].astype("string")
    + "-W"
    + filtered_df["week"].astype("string").str.zfill(2)
)
filtered_df["month_label"] = filtered_df["date"].dt.to_period("M").astype("string")
filtered_df["year_label"] = filtered_df["date"].dt.year.astype("Int64").astype("string")

filter_columns = st.columns(6)

with filter_columns[0]:
    volume_options = ["All"] + sorted(filtered_df["volume"].dropna().astype(str).unique().tolist())
    selected_volume = st.selectbox("Package Volume", volume_options, key="summary_volume")

with filter_columns[1]:
    product_options = ["All"] + sorted(filtered_df["product"].dropna().astype(str).unique().tolist())
    selected_product = st.selectbox("Product", product_options, key="summary_product")

with filter_columns[2]:
    date_options = ["All"] + sorted(
        filtered_df["date"].dropna().dt.strftime("%Y-%m-%d").unique().tolist(),
        reverse=True,
    )
    selected_date = st.selectbox("Date", date_options, key="summary_date")

with filter_columns[3]:
    week_options = ["All"] + sorted(filtered_df["week_label"].dropna().unique().tolist(), reverse=True)
    selected_week = st.selectbox("Week", week_options, key="summary_week")

with filter_columns[4]:
    month_options = ["All"] + sorted(filtered_df["month_label"].dropna().unique().tolist(), reverse=True)
    selected_month = st.selectbox("Month", month_options, key="summary_month")

with filter_columns[5]:
    year_options = ["All"] + sorted(filtered_df["year_label"].dropna().unique().tolist(), reverse=True)
    selected_year = st.selectbox("Year", year_options, key="summary_year")

if selected_volume != "All":
    filtered_df = filtered_df[filtered_df["volume"].astype(str) == selected_volume]
if selected_product != "All":
    filtered_df = filtered_df[filtered_df["product"].astype(str) == selected_product]
if selected_date != "All":
    filtered_df = filtered_df[filtered_df["date"].dt.strftime("%Y-%m-%d") == selected_date]
if selected_week != "All":
    filtered_df = filtered_df[filtered_df["week_label"] == selected_week]
if selected_month != "All":
    filtered_df = filtered_df[filtered_df["month_label"] == selected_month]
if selected_year != "All":
    filtered_df = filtered_df[filtered_df["year_label"] == selected_year]

has_active_filter = any(
    selected_filter != "All"
    for selected_filter in [
        selected_volume,
        selected_product,
        selected_date,
        selected_week,
        selected_month,
        selected_year,
    ]
)

with st.expander("🗑️ Delete Record"):
    if not has_active_filter:
        st.info("Select a filter before choosing a record to delete.")
    elif filtered_df.empty:
        st.info("No records match the selected filters.")
    else:
        delete_options = [None] + filtered_df[["date", "product", "market", "final_counts"]].astype(str).apply(lambda x: "-".join(x), axis=1).tolist()
        selected_delete_id = st.selectbox(
            "Select a record to delete",
            delete_options,
            format_func=lambda record_id: "Select a record" if record_id is None else str(record_id),
        )

        if selected_delete_id is not None:
            confirm_delete = st.checkbox("I confirm that I want to delete this record.")

            if st.button("Delete selected record", type="secondary"):
                if not confirm_delete:
                    st.warning("Please confirm deletion first.")
                else:
                    delete_record(selected_delete_id)
                    st.success(f"Record {selected_delete_id} deleted successfully.")
                    for filter_key in [
                        "summary_volume",
                        "summary_product",
                        "summary_date",
                        "summary_week",
                        "summary_month",
                        "summary_year",
                    ]:
                        st.session_state.pop(filter_key, None)
                    st.rerun()

if filtered_df.empty:
    st.info("No records match the selected filters.")

weekly_table = (
    filtered_df.pivot_table(
        index=["week_label", "product"],
        columns="market",
        values=[
            "initial_average_counts",
            "final_counts"
        ],
        aggfunc="mean"
    )
    .round(2)
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
        "Export by",
        ["All records", "Date", "Week", "Month", "Year"],
        index=0,
    )

    if period_filter == "Date":
        date_options = ["All"] + sorted(
            export_df["date"].dt.strftime("%Y-%m-%d").dropna().unique().tolist()
        )
        selected_period = st.selectbox(
            "Select date",
            date_options,
            format_func=lambda value: value if value == "All" else pd.to_datetime(value).strftime("%Y-%m-%d")
        )
        if selected_period != "All":
            export_df = export_df[export_df["date"].dt.strftime("%Y-%m-%d") == selected_period]

    elif period_filter == "Week":
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

    if period_filter != "All records":
        export_df = export_df.drop(columns=[col for col in ["week_label", "month_label", "year_label"] if col in export_df.columns], errors="ignore")

export_buffer = BytesIO()


def create_excel_report(output, data_frame):
    export_data = data_frame.copy()
    if "date" in export_data.columns:
        export_data["date"] = pd.to_datetime(export_data["date"], errors="coerce")
        export_data["date"] = export_data["date"].dt.strftime("%Y-%m-%d")

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        export_data.to_excel(writer, sheet_name="Filtered Records", index=False)
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
                len(export_data),
                round(export_data["initial_average_counts"].mean(), 2) if "initial_average_counts" in export_data.columns else 0,
                round(export_data["final_counts"].mean(), 2) if "final_counts" in export_data.columns else 0,
            ],
        })
        overview.to_excel(writer, sheet_name="Overview", index=False)


# Keep a current master workbook on the server for future downloads.
export_folder = Path("exports")
export_folder.mkdir(exist_ok=True)
master_export = export_folder / "QC_Dashboard.xlsx"


export_buffer.seek(0)

selected_label = "all-records"
if "period_filter" in locals() and period_filter != "All records":
    if period_filter == "Date":
        selected_label = pd.to_datetime(selected_period).strftime("%Y-%m-%d")
    else:
        selected_label = str(selected_period).replace("/", "-")

st.download_button(
    label="Download Excel report",
    data=export_buffer.getvalue(),
    file_name=f"{selected_label}.xlsx",
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
