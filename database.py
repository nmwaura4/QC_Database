import sqlite3
import pandas as pd
from config import DATABASE

# =====================================================
# DATABASE CONNECTION
# =====================================================

def get_connection():
    return sqlite3.connect(
        DATABASE,
        check_same_thread=False
    )


# =====================================================
# INITIALIZE DATABASE
# =====================================================

def initialize_database():

    conn = get_connection()
    cursor = conn.cursor()

    # ---------------- Users Table ----------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        week INTEGER,
        date TEXT,
        product TEXT,
        market TEXT,
        initial_average_counts INTEGER,
        final_counts INTEGER,
        benchmark INTEGER,
        remarks TEXT

    )
    """)
    #====================================================
    # SAFE SCHEMA UPDATE 
    #====================================================

    cursor.execute("PRAGMA table_info(users)")
    existing_columns = [column[1].lower() for column in cursor.fetchall()]

    if "volume" not in existing_columns:
        cursor.execute("""
        ALTER TABLE users
        ADD COLUMN volume TEXT
        """)

    if "customer_name" not in existing_columns:
        cursor.execute("""
        ALTER TABLE users
        ADD COLUMN customer_name TEXT
        """)

    if "phytoseiulus_bulk" not in existing_columns:
        cursor.execute("""
        ALTER TABLE users
        ADD COLUMN phytoseiulus_bulk TEXT
        """)

    bulk_columns = {
        "live_pred": "INTEGER",
        "dead_pred": "INTEGER",
        "live_rsm": "INTEGER",
        "dead_rsm": "INTEGER",
        "live_pred_percentage": "REAL",
        "dead_pred_percentage": "REAL",
        "live_rsm_percentage": "REAL",
        "dead_rsm_percentage": "REAL",
    }
    for column_name, column_type in bulk_columns.items():
        if column_name not in existing_columns:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}")
    #=====================
    #  Accounts Table 
    #=====================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accounts(

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT

    )
    """)

    cursor.execute("PRAGMA table_info(accounts)")
    account_columns = [column[1].lower() for column in cursor.fetchall()]

    if "email" not in account_columns:
        cursor.execute("ALTER TABLE accounts ADD COLUMN email TEXT")
    if "password" not in account_columns:
        cursor.execute("ALTER TABLE accounts ADD COLUMN password TEXT")
    #=========================
    # Default Admin 
    #=========================

    cursor.execute("""
    INSERT OR IGNORE INTO accounts
    (email, password, role)
    VALUES
    ('admin@example.com', 'Password1!', 'Administrator')
    """)

    conn.commit()
    conn.close()
# ==========
# LOGIN
# ==========

def login(email, password):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role
        FROM accounts
        WHERE email = ?
        AND password = ?
    """, (email, password))

    user = cursor.fetchone()

    conn.close()

    return user

# ================
# ADD RECORD
# ================

def add_record(
    week,
    date,
    product,
    market,
    initial_average,
    final_counts,
    benchmark,
    remarks
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO records( 

        week,
        date,
        product,
        market,
        initial_average,
        final_counts,
        benchmark,
        remarks

    )

    VALUES(?,?,?,?,?,?,?,?)

    """, (

        week,
        date,
        product,
        market,
        initial_average,
        final_counts,
        benchmark,
        remarks

    ))

    conn.commit()
    conn.close()


# ==============
# GET RECORDS
# ==============

def get_records():

    conn = get_connection()

    df = pd.read_sql_query(

        "SELECT * FROM records ORDER BY id DESC",

        conn

    )

    conn.close()

    return df


# ==============
# DELETE RECORD
# ==============

def delete_record(record_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(

        "DELETE FROM users WHERE id=?",

        (record_id,)

    )

    conn.commit()
    conn.close()


# ==============
# UPDATE RECORD
# ==============

def update_record(

    record_id,
    week,
    date,
    product,
    market,
    initial_average,
    final_counts,
    benchmark,
    remarks

):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

    UPDATE records

    SET

        week=?,
        date=?,
        product=?,
        market=?,
        initial_average=?,
        final_counts=?,
        benchmark=?,
        remarks=?

    WHERE id=?

    """, (

        week,
        date,
        product,
        market,
        initial_average,
        final_counts,
        benchmark,
        remarks,
        record_id

    ))

    conn.commit()
    conn.close()