import sqlite3

import pandas as pd
import streamlit as st

from database import get_connection


if not st.session_state.get("logged_in", False):
    st.switch_page("app.py")
    st.stop()

if st.session_state.get("role") != "Administrator":
    st.error("Only administrators can manage users.")
    st.stop()


def get_accounts():
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT id, email, role FROM accounts ORDER BY id"
        ).fetchall()
    finally:
        conn.close()


def add_account(email, password, role):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO accounts (email, password, role) VALUES (?, ?, ?)",
            (email, password, role),
        )
        conn.commit()
        return True, "User added successfully."
    except sqlite3.IntegrityError:
        return False, "That email already exists."
    finally:
        conn.close()


def update_account(user_id, new_password, role):
    conn = get_connection()
    try:
        if new_password:
            conn.execute(
                "UPDATE accounts SET password = ?, role = ? WHERE id = ?",
                (new_password, role, user_id),
            )
        else:
            conn.execute("UPDATE accounts SET role = ? WHERE id = ?", (role, user_id))
        conn.commit()
        return True, "User updated successfully."
    except sqlite3.Error as exc:
        return False, f"Failed to update user: {exc}"
    finally:
        conn.close()


def delete_account(user_id, admin_password):
    conn = get_connection()
    try:
        valid_admin = conn.execute(
            "SELECT 1 FROM accounts WHERE role = 'Administrator' AND password = ? LIMIT 1",
            (admin_password,),
        ).fetchone()
        if valid_admin is None:
            return False, "A valid Administrator password is required to delete users."

        account = conn.execute(
            "SELECT email FROM accounts WHERE id = ?", (user_id,)
        ).fetchone()
        if account and account[0] == "admin@example.com":
            return False, "The default admin account cannot be deleted."

        conn.execute("DELETE FROM accounts WHERE id = ?", (user_id,))
        conn.commit()
        return True, "User deleted successfully."
    except sqlite3.Error as exc:
        return False, f"Failed to delete user: {exc}"
    finally:
        conn.close()


st.title("👤 User Management")
st.caption("Add, update, or remove users from the QC Database application.")

with st.form("add_user_form"):
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    role = st.text_input("Role", placeholder="e.g. Technician or Analyst")
    submitted = st.form_submit_button("Add User")

    if submitted:
        if not email.strip() or not password.strip() or not role.strip():
            st.warning("Email, password, and role are required.")
        else:
            success, message = add_account(email.strip(), password.strip(), role.strip())
            (st.success if success else st.error)(message)
            if success:
                st.rerun()

st.divider()
st.subheader("Existing Users")
accounts = get_accounts()
if accounts:
    st.dataframe(
        pd.DataFrame(accounts, columns=["ID", "Email", "Role"]),
        use_container_width=True,
        hide_index=True,
    )

    st.divider()
    st.subheader("Update or Remove a User")
    selected_email = st.selectbox("Select user", [row[1] for row in accounts])
    selected_user = next(row for row in accounts if row[1] == selected_email)

    with st.form("edit_user_form"):
        new_password = st.text_input("New password", type="password")
        new_role = st.text_input("Role", value=selected_user[2] or "")
        admin_password = st.text_input("Administrator password to confirm deletion", type="password")
        update_submitted = st.form_submit_button("Update User")
        delete_submitted = st.form_submit_button("Delete User")

        if update_submitted:
            success, message = update_account(selected_user[0], new_password.strip(), new_role.strip())
            (st.success if success else st.error)(message)
            if success:
                st.rerun()
        elif delete_submitted:
            success, message = delete_account(selected_user[0], admin_password)
            (st.success if success else st.error)(message)
            if success:
                st.rerun()
else:
    st.info("No users have been added yet.")