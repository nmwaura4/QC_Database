from matplotlib import style
import streamlit as st
from pathlib import Path

from auth import login
from assets.style import load_css
from database import initialize_database
from config import APP_TITLE
from sidebar import show_sidebar

show_sidebar()

st.markdown("""
<style>
.stApp {    background-color: lightnavyblue;   
             color: white;  
              font-family: Arial,
             sans-serif;    
            padding: 20px;   
             border-radius: 10px;   
             box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);  
              transition: background-color 0.3s ease, color 0.3s ease; 
               text-align: center;  
              margin-bottom: 20px;   
             font-size: 18px;   
             line-height: 1.6;
}   
</style>)
            
<style>
.stButton > button {
    background-color: #007BFF;
    color: white;
    border-radius: 10px;
    font-weight: bold;
}
.stButton > button:hover {
    background-color: #0056b3;
}
</style>
""", unsafe_allow_html=True)

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title=APP_TITLE,
    layout="wide"
)

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

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        user = login(username, password)

        if user:
            st.session_state.logged_in = True
            st.session_state.role = user[0]
            st.rerun()

        else:
            st.error("Invalid username or password.")

    st.stop()


# ---------------- MAIN PAGE ----------------

st.title(APP_TITLE)

st.success("Welcome user! You are logged in as admin.")

st.write("""
Welcome to the QC Database Management System.

Select a page from the sidebar to begin.""")

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

    
