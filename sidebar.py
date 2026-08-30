import streamlit as st
from pathlib import Path

def show_sidebar():
    with st.sidebar:

        logo_path = Path(__file__).parent / "assets" / "QC_Database_Logo.png"

        if logo_path.exists():
            st.image(str(logo_path), width=180)

        st.title("QC Database")
        st.write("---")
        st.success("🟢 System Online")
        st.caption("Version 1.0")

        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.rerun()

