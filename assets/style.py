import streamlit as st

def load_css():
    st.markdown("""
    <style>

    .main{
        padding-top:1rem;
    }

    div[data-testid="stMetric"]{
        background:#f8f9fa;
        padding:20px;
        border-radius:10px;
    }
try:
    st.image("assets/logo.png", width=180)
except Exception:
    st.info("Company logo not found.")
    </style>
                
    """, unsafe_allow_html=True)