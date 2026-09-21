import time

import streamlit as st

from assets.style import load_css
from auth import login
from config import APP_TITLE
from database import initialize_database
from sidebar import show_sidebar

SESSION_TIMEOUT_SECONDS = 10 * 60


@st.fragment(run_every="60s")
def enforce_session_timeout():
    if (
        st.session_state.get("logged_in", False)
        and time.monotonic() - st.session_state.get("last_activity", 0)
        >= SESSION_TIMEOUT_SECONDS
    ):
        st.session_state.clear()
        st.rerun()


st.set_page_config(page_title=APP_TITLE, layout="wide")
show_sidebar()
load_css()
initialize_database()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    enforce_session_timeout()

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
            st.session_state.last_activity = time.monotonic()
            st.rerun()
        else:
            st.error("Invalid email or password.")
    st.stop()


available_pages = [
    st.Page("pages/Home.py", title="Home", default=True),
    st.Page("pages/Dashboard.py", title="Dashboard"),
    st.Page("pages/Record.py", title="QC Record"),
]

if st.session_state.get("role") == "Administrator":
    available_pages.append(st.Page("pages/Users.py", title="User Management"))

st.navigation(available_pages).run()


from auth import login

