import streamlit as st
import pandas as pd
from datetime import date
from pathlib import Path
from database import get_connection
import streamlit as st
from sidebar import show_sidebar
show_sidebar()


if not st.session_state.get("logged_in", False):
    st.switch_page("app.py")  
    st.stop()

    
st.title("➕ Add QC Record")
st.caption("Quality Control Data Entry")

conn = get_connection()
cursor = conn.cursor()

with st.form("qc_form"):

    left, right = st.columns(2)

    with left:

        record_date = st.date_input(
            "Date",
            value=date.today()
        )

        product = st.selectbox(
            "Product",
            ["Montdorensis", "Californicus", "Cucumeris", "Swirskii", "Hypoaspis", "Phytoseiulus", "Other"]
        )

        market = st.selectbox(
            "Market",
            ["Export", "Local"]
        )
        customer = st.text_input("Customer Name")

        volume = st.selectbox(
            "Package Volume",
            [   "1,000",
                "5,000",
                "10,000",
                "12,500",
                "25,000",
                "50,000",
                "100,000",
                "200,000",
                "250,000",
                "1,000,000"
            ]
        )

        initial_average = st.number_input(
            "Initial Average Counts",
            min_value=0,
            value=0
        )

    with right:

        week = record_date.isocalendar().week

        st.info(f"Week {week}")

        final_counts = st.number_input(
            "Final Counts",
            min_value=0,
            value=0
        )

        benchmark = st.selectbox(
            "Benchmark",
            [
                "1000",
                "10,000",
                "12,500",
                "25,000",
                "50,000",
                "125,000",
                "200,000",
                "250,000",
                "500,000",
                "1,000,000"
            ]
        )

        remarks = st.text_area("Remarks")

    submitted = st.form_submit_button("💾 Save Record")

    if submitted:

        if product.strip() == "":
            st.error("Product cannot be empty.")

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
st.subheader("Edit Existing Record")

records_df = pd.read_sql_query(
    "SELECT * FROM users ORDER BY id DESC",
    conn
)

if "date" in records_df.columns:
    records_df["date"] = pd.to_datetime(records_df["date"], errors="coerce").dt.strftime("%Y-%m-%d")

if records_df.empty:
    st.info("There are no records to edit yet.")
else:
    record_options = records_df["id"].tolist()
    selected_id = st.selectbox(
        "Select record ID",
        record_options,
        format_func=lambda record_id: f"Record {record_id}"
    )
    selected_record = records_df.loc[
        records_df["id"] == selected_id
    ].iloc[0]

    with st.form("edit_qc_form"):
        edit_left, edit_right = st.columns(2)

        with edit_left:
            edit_date = st.date_input(
                "Date",
                value=date.fromisoformat(str(selected_record["date"]))
            )
            edit_product = st.selectbox(
                "Product",
                ["Montdorensis", "Californicus", "Cucumeris", "Swirskii", "Hypoaspis", "Phytoseiulus", "Other"],
                index=["Montdorensis", "Californicus", "Cucumeris", "Swirskii", "Hypoaspis", "Phytoseiulus", "Other"].index(selected_record["product"])
                if selected_record["product"] in ["Montdorensis", "Californicus", "Cucumeris", "Swirskii", "Hypoaspis", "Phytoseiulus", "Other"] else 0
            )
            edit_market = st.selectbox(
                "Market",
                ["Export", "Local"],
                index=["Export", "Local"].index(selected_record["market"])
                if selected_record["market"] in ["Export", "Local"] else 0
            )
            edit_customer = st.text_input(
                "Customer Name",
                value=str(selected_record.get("customer_name", "") or "")
            )
            volume_options = ["1,000", "5,000", "10,000", "12,500", "25,000", "50,000", "100,000", "200,000", "250,000", "1,000,000"]
            edit_volume = st.selectbox(
                "Package Volume",
                volume_options,
                index=volume_options.index(selected_record["volume"])
                if selected_record["volume"] in volume_options else 0
            )
            edit_initial_average = st.number_input(
                "Initial Average Counts",
                min_value=0,
                value=int(selected_record["initial_average_counts"] or 0)
            )

        with edit_right:
            edit_week = edit_date.isocalendar().week
            st.info(f"Week {edit_week}")
            edit_final_counts = st.number_input(
                "Final Counts",
                min_value=0,
                value=int(selected_record["final_counts"] or 0)
            )
            benchmark_options = ["1000", "10,000", "12,500", "25,000", "50,000", "125,000", "200,000", "250,000", "500,000", "1,000,000"]
            edit_benchmark = st.selectbox(
                "Benchmark",
                benchmark_options,
                index=benchmark_options.index(str(selected_record["benchmark"]))
                if str(selected_record["benchmark"]) in benchmark_options else 0
            )
            edit_remarks = st.text_area(
                "Remarks",
                value=str(selected_record["remarks"] or "")
            )

        update_submitted = st.form_submit_button("✏️ Update Record")

        if update_submitted:
            if edit_product.strip() == "":
                st.error("Product cannot be empty.")
            else:
                cursor.execute("""
                SELECT id FROM users
                WHERE date=? AND product=? AND market=? AND customer_name=?
                  AND volume=? AND initial_average_counts=? AND final_counts=?
                  AND benchmark=? AND remarks=? AND id<>?
                LIMIT 1
                """, (
                    str(edit_date),
                    edit_product,
                    edit_market,
                    edit_customer,
                    edit_volume,
                    edit_initial_average,
                    edit_final_counts,
                    edit_benchmark,
                    edit_remarks,
                    selected_id
                ))
                duplicate_record = cursor.fetchone()

                if duplicate_record:
                    st.warning(
                        f"These details already exist as record {duplicate_record[0]}."
                    )
                else:
                    cursor.execute("""
                    UPDATE users
                    SET week=?, date=?, product=?, market=?, customer_name=?, volume=?,
                        initial_average_counts=?, final_counts=?, benchmark=?, remarks=?
                    WHERE id=?
                    """, (
                        edit_week,
                        str(edit_date),
                        edit_product,
                        edit_market,
                        edit_customer,
                        edit_volume,
                        edit_initial_average,
                        edit_final_counts,
                        edit_benchmark,
                        edit_remarks,
                        selected_id
                    ))
                    conn.commit()

                    export_folder = Path("exports")
                    export_folder.mkdir(exist_ok=True)
                    updated_df = pd.read_sql_query(
                        "SELECT * FROM users",
                        conn
                    )
                    if "date" in updated_df.columns:
                        updated_df["date"] = pd.to_datetime(updated_df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
                    updated_df.to_excel(
                        export_folder / "QC_Database.xlsx",
                        index=False
                    )

                    st.success("✅ Record Updated Successfully")

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