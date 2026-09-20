import sqlite3
import streamlit as st
import pandas as pd

from database import get_connection


if not st.session_state.get("logged_in", False):
    st.switch_page("app.py")
    st.stop()


if st.session_state.get("role") != "Administrator":
    st.error("Only administrators can manage users.")
    st.stop()


st.title("👤 User Management")
st.caption("Add, update, or remove users from the QC Database application.")


def get_accounts():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id,email, role FROM accounts ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    return rows


def add_account(email, password, role):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT 1 FROM accounts WHERE password = ? LIMIT 1",
            (password,),
        )
        if cursor.fetchone() is not None:
            return False, "That password is already assigned to another user."

        cursor.execute(
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
    cursor = conn.cursor()

    try:
        if new_password:
            cursor.execute(
                """
                SELECT 1
                FROM accounts
                WHERE password = ? AND id != ?
                LIMIT 1
                """,
                (new_password, user_id),
            )
            if cursor.fetchone() is not None:
                return False, "That password is already assigned to another user."

            cursor.execute(
                "UPDATE accounts SET password = ?, role = ? WHERE id = ?",
                (new_password, role, user_id),
            )
        else:
            cursor.execute(
                "UPDATE accounts SET role = ? WHERE id = ?",
                (role, user_id),
            )
        conn.commit()
        return True, "User updated successfully."
    except Exception as exc:
        return False, f"Failed to update user: {exc}"
    finally:
        conn.close()


def delete_account(user_id, admin_password):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT 1
            FROM accounts
            WHERE role = 'Administrator' AND password = ?
            LIMIT 1
            """,
            (admin_password,),
        )
        if cursor.fetchone() is None:
            return False, "A valid Administrator password is required to delete users."

        cursor.execute(
            "SELECT email, username FROM accounts WHERE id = ?",
            (user_id,),
        )
        user = cursor.fetchone()

        if user and (user[0] == "admin@example.com" or user[1] == "admin"):
            return False, "The default admin account cannot be deleted."

        cursor.execute("DELETE FROM accounts WHERE id = ?", (user_id,))
        conn.commit()
        return True, "User deleted successfully."
    except Exception as exc:
        return False, f"Failed to delete user: {exc}"
    finally:
        conn.close()


with st.form("add_user_form"):
    email= st.text_input("Email")
    password = st.text_input(
        "Password",
        type="password",
        help="Password must be at least 8 characters long and contain at least one uppercase letter.",
    )
    role = st.text_input(
        "Role",
        placeholder="e.g. Technician or Analyst",
        help="Enter a role such as Administrator, Technician, or Analyst.",
    )
    submitted = st.form_submit_button("Add User")

    if submitted:
        if not email.strip() or not password.strip() or not role.strip():
            st.warning("Email, password, and role are required.")
        else:
            success, message = add_account(
                email.strip(), password.strip(), role.strip()
            )
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)


st.divider()
st.subheader("Existing Users")

accounts = get_accounts()
if accounts:
    df = pd.DataFrame(accounts, columns=["ID", "Email", "Role"])
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No users have been added yet.")


st.divider()
st.subheader("Update or Remove a User")

if accounts:
    emails = [row[1] for row in accounts]
    selected_email = st.selectbox("Select user", emails)
    selected_user = next(row for row in accounts if row[1] == selected_email)

    with st.form("edit_user_form"):
        user_id = selected_user[0]
        current_role = selected_user[2]

        new_password = st.text_input(
            "New password",
            type="password",
            help="Leave blank to keep the current password.",
        )
        new_role = st.text_input(
            "Role",
            value=current_role or "",
            placeholder="e.g. Technician or Analyst",
            help="Enter a role such as Administrator, Technician, or Analyst.",
        )
        admin_password = st.text_input(
            "Administrator password to confirm deletion",
            type="password",
            help="Required only when deleting a user.",
        )

        col1, col2 = st.columns(2)
        with col1:
            update_submitted = st.form_submit_button("Update User")
        with col2:
            delete_submitted = st.form_submit_button("Delete User")

        if update_submitted:
            if not new_role.strip():
                st.warning("Role is required.")
            else:
                success, message = update_account(
                    user_id, new_password.strip(), new_role.strip()
                )
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

        if delete_submitted:
            success, message = delete_account(user_id, admin_password.strip())
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
else:
    st.info("Add a user first to enable updates and deletion.")
