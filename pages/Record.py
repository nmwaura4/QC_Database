import streamlit as st
import pandas as pd
from datetime import date
from pathlib import Path
from database import get_connection
import streamlit as st
from sidebar import show_sidebar
show_sidebar()


if not st.session_state.get("logged_in", False):
    st.switch_page("Dashboard.py")  
    st.stop()

    
st.title("➕ Add QC Record")
st.caption("Quality Control Data Entry")
st.caption("Fields marked with * are mandatory.")

conn = get_connection()
cursor = conn.cursor()

product_options = [
    "Montdorensis", "Californicus", "Cucumeris", "Swirskii",
    "Hypoaspis", "Phytoseiulus", "lacewings", "Other"
]
market_options = ["Export", "Local"]
customer_options = [
    "Biobest ", "Sher", "Uganda", "Tanzania", "V.D berg", "Timaflor1",
    "Timaflor2", "Timaflor 3", "Timaflor 4", "Timaflor 5", "Timaflor 6",
    "Timaflor 7", "lolomarik1", "Lolomarik 2", "Penta", "Selecta kenya",
    "De Reuiters", "Uhuru", "Olnjorowa", "Dudutech", "Kongngoni", "Bigot",
    "Flamingo", "United selection", "Cash customer"
]
volume_options = [
    "1,000", "5,000", "10,000", "12,500", "25,000", "50,000",
    "100,000", "200,000", "250,000", "1,000,000"
]
benchmark_options = [
    "1000", "10,000", "12,500", "25,000", "50,000", "125,000",
    "200,000", "250,000", "500,000", "1,000,000"
]
required_option = "Select..."
product_options = [required_option] + product_options
market_options = [required_option] + market_options
customer_options = [required_option] + customer_options
volume_options = [required_option] + volume_options
benchmark_options = [required_option] + benchmark_options

with st.form("qc_form"):

    left, right = st.columns(2)

    with left:

        record_date = st.date_input(
            "Date *",
            value=date.today()
        )

        product = st.selectbox(
            "Product *", product_options
        )

        market = st.selectbox("Market *", market_options)
        customer = st.selectbox("Customer *", customer_options)

        volume = st.selectbox("Package Volume *", volume_options)

        initial_average = st.number_input(
            "Initial Average Counts *",
            min_value=0,
            value=0
        )

    with right:

        week = record_date.isocalendar().week

        st.info(f"Week {week}")

        final_counts = st.number_input(
            "Final Counts *",
            min_value=0,
            value=0
        )

        benchmark = st.selectbox("Benchmark *", benchmark_options)

        remarks = st.text_area(
            "Remarks (optional)",
            placeholder="Write any observations, issues, or customer feedback...",
            height=120,
        )

    submitted = st.form_submit_button("💾 Save Record")

    if submitted:

        required_values = {
            "Product": product,
            "Market": market,
            "Customer": customer,
            "Package Volume": volume,
            "Benchmark": benchmark,
        }
        missing_fields = [
            field_name
            for field_name, field_value in required_values.items()
            if field_value == required_option
        ]

        if missing_fields:
            st.error(
                "Please complete the required fields: "
                + ", ".join(missing_fields)
                + "."
            )

        else:
            cursor.execute("""
            SELECT id FROM users
            WHERE date=? AND product=? AND market=? AND customer_name=?
              AND volume=? AND initial_average_counts=? AND final_counts=?
              AND benchmark=? AND remarks=?
            LIMIT 1
            """, (
                str(record_date),
                product,
                market,
                customer,
                volume,
                initial_average,
                final_counts,
                benchmark,
                remarks
            ))
            duplicate_record = cursor.fetchone()

            if duplicate_record:
                st.warning(
                    f"This entry already exists as record {duplicate_record[0]}."
                )
            else:
                cursor.execute("""
                INSERT INTO users
                (
                    week,
                    date,
                    product,
                    market,
                    customer_name,
                    volume,
                    initial_average_counts,
                    final_counts,
                    benchmark,
                    remarks
                )

                VALUES
                (?,?,?,?,?,?,?,?,?,?)
                """,

                (
                    week,
                    str(record_date),
                    product,
                    market,
                    customer,
                    volume,
                    initial_average,
                    final_counts,
                    benchmark,
                    remarks
                ))

                conn.commit()

                df = pd.read_sql_query(
                    "SELECT * FROM users",
                    conn
                )
                if "date" in df.columns:
                    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")

                # Create exports folder if it doesn't exist
                export_folder = Path("exports")
                export_folder.mkdir(exist_ok=True)

                df.to_excel(
                    export_folder / "QC_Database.xlsx",
                    index=False
                )

                st.success("✅ Record Saved Successfully")

st.divider()
st.subheader("Edit Existing Records")

records_df = pd.read_sql_query(
    "SELECT * FROM users ORDER BY id DESC",
    conn
)

if records_df.empty:
    st.info("There are no records to edit yet.")
else:
    record_dates = pd.to_datetime(records_df["date"], errors="coerce")
    filter_columns = st.columns(4)

    with filter_columns[0]:
        date_options = ["All"] + sorted(
            record_dates.dropna().dt.strftime("%Y-%m-%d").unique().tolist(),
            reverse=True,
        )
        selected_date = st.selectbox("Filter by Date", date_options)

    with filter_columns[1]:
        product_filter_options = ["All"] + sorted(
            records_df["product"].dropna().astype(str).unique().tolist()
        )
        selected_product = st.selectbox("Filter by Product", product_filter_options)

    with filter_columns[2]:
        month_options = ["All"] + sorted(
            record_dates.dropna().dt.to_period("M").astype(str).unique().tolist(),
            reverse=True,
        )
        selected_month = st.selectbox("Filter by Month", month_options)

    with filter_columns[3]:
        year_options = ["All"] + sorted(
            record_dates.dropna().dt.year.astype(str).unique().tolist(),
            reverse=True,
        )
        selected_year = st.selectbox("Filter by Year", year_options)

    hide_edit_data = st.checkbox("Hide data after editing", key="hide_edit_data")

    record_mask = pd.Series(True, index=records_df.index)
    if selected_date != "All":
        record_mask &= record_dates.dt.strftime("%Y-%m-%d") == selected_date
    if selected_product != "All":
        record_mask &= records_df["product"].astype(str) == selected_product
    if selected_month != "All":
        record_mask &= record_dates.dt.to_period("M").astype(str) == selected_month
    if selected_year != "All":
        record_mask &= record_dates.dt.year.astype(str) == selected_year

    filtered_records = records_df.loc[record_mask].copy()
    has_edit_filter = any(
        selected_filter != "All"
        for selected_filter in [selected_date, selected_product, selected_month, selected_year]
    )

    if not has_edit_filter:
        st.info("Select a date, product, month, or year to access records for editing.")
    elif hide_edit_data:
        st.info("Edit data is hidden. Uncheck 'Hide data after editing' to show it again.")
    elif filtered_records.empty:
        st.info("No records match the selected filters.")
    else:
        edit_table = filtered_records[[
            "id", "date", "product", "market", "customer_name", "volume",
            "initial_average_counts", "final_counts", "benchmark", "remarks"
        ]].copy()
        edit_table["date"] = pd.to_datetime(edit_table["date"], errors="coerce").dt.date
        edit_table["initial_average_counts"] = edit_table["initial_average_counts"].fillna(0).astype(int)
        edit_table["final_counts"] = edit_table["final_counts"].fillna(0).astype(int)
        for column in ["product", "market", "customer_name", "volume", "benchmark", "remarks"]:
            edit_table[column] = edit_table[column].fillna("").astype(str)

        record_ids = tuple(edit_table["id"].astype(int).tolist())
        editor_key = (
            f"edit_table_{selected_date}_{selected_product}_{selected_month}_"
            f"{selected_year}_{record_ids}_{st.session_state.get('edit_table_version', 0)}"
        )
        edited_records = st.data_editor(
            edit_table,
            hide_index=True,
            num_rows="dynamic",
            width="stretch",
            disabled=["id"],
            key=editor_key,
            column_config={
                "id": None,
                "date": st.column_config.DateColumn("Date", required=True),
                "product": st.column_config.SelectboxColumn("Product", options=product_options, required=True),
                "market": st.column_config.SelectboxColumn("Market", options=market_options, required=True),
                "customer_name": st.column_config.SelectboxColumn("Customer Name", options=customer_options),
                "volume": st.column_config.SelectboxColumn("Package Volume", options=volume_options),
                "initial_average_counts": st.column_config.NumberColumn("Initial Average Counts", min_value=0, step=1),
                "final_counts": st.column_config.NumberColumn("Final Counts", min_value=0, step=1),
                "benchmark": st.column_config.SelectboxColumn("Benchmark", options=benchmark_options),
                "remarks": st.column_config.TextColumn("Remarks"),
            },
        )

        if st.button("✏️ Update Records", type="primary"):
            updated_count = 0
            inserted_count = 0
            errors = []

            for _, edited_values in edited_records.iterrows():
                parsed_date = pd.to_datetime(edited_values["date"], errors="coerce")
                edit_product = str(edited_values["product"]).strip()
                record_id = edited_values["id"]

                if pd.isna(parsed_date) or not edit_product:
                    record_label = "new row" if pd.isna(record_id) else f"Record {int(record_id)}"
                    errors.append(f"{record_label} needs a valid date and product.")
                    continue

                edit_date = parsed_date.date()
                initial_average = edited_values["initial_average_counts"]
                final_counts = edited_values["final_counts"]
                if pd.isna(initial_average):
                    initial_average = 0
                if pd.isna(final_counts):
                    final_counts = 0
                values = [
                    edit_date.isocalendar().week,
                    str(edit_date),
                    edit_product,
                    str(edited_values["market"]),
                    str(edited_values["customer_name"]),
                    str(edited_values["volume"]),
                    int(initial_average),
                    int(final_counts),
                    str(edited_values["benchmark"]),
                    str(edited_values["remarks"]),
                ]

                if pd.isna(record_id):
                    cursor.execute("""
                    INSERT INTO users
                    (week, date, product, market, customer_name, volume,
                     initial_average_counts, final_counts, benchmark, remarks)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, values)
                    inserted_count += 1
                else:
                    cursor.execute("""
                    UPDATE users
                    SET week=?, date=?, product=?, market=?, customer_name=?, volume=?,
                        initial_average_counts=?, final_counts=?, benchmark=?, remarks=?
                    WHERE id=?
                    """, [*values, int(record_id)])
                    updated_count += 1

            if errors:
                for error in errors:
                    st.warning(error)
            if updated_count or inserted_count:
                conn.commit()
                export_folder = Path("exports")
                export_folder.mkdir(exist_ok=True)
                updated_df = pd.read_sql_query("SELECT * FROM users", conn)
                updated_df["date"] = pd.to_datetime(updated_df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
                updated_df.to_excel(export_folder / "QC_Database.xlsx", index=False)
                st.success(
                    f"✅ {updated_count} record(s) updated and "
                    f"{inserted_count} new record(s) saved successfully."
                )
                st.session_state.edit_table_version = st.session_state.get("edit_table_version", 0) + 1
                st.rerun()

conn.close()

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