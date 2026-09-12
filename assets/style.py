import streamlit as st

def load_css():
    st.markdown("""
    <style>

    .main{
        padding-top:1rem;
    }

    div[data-testid="stMetric"]{
        background:lightblue;
        border:1px solid lightsblue;
        padding:20px;
        border-radius:10px;
    }

    div[data-testid="stMetricLabel"],
    div[data-testid="stMetricLabel"] * {
             color:green !important;
    }

    div[data-testid="stCaptionContainer"],
    div[data-testid="stCaptionContainer"] * {
        color: white !important;
        font-size: 1.5rem;
        font-weight: 600;
    }
    div[data-testid="stMetricValue"] {
        color:midnightblue !important;
    }

    .metric-card {
        min-height:132px;
        background:lightgray;
        border:1px solid lightsblue;
        padding:18px;
        border-radius:10px;
    }

    .metric-label {
        color:black;
        font-size:0.9rem;
        font-weight:600;
    }

    .metric-value {
        color:green;
        font-size:2rem;
        line-height:1.2;
        margin:8px 0;
    }

    .metric-description {
        color:black;
        font-size:0.78rem;
        line-height:1.35;
    }
    </style>
    """, unsafe_allow_html=True)