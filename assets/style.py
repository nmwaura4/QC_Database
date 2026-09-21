import streamlit as st

def load_css():
    st.markdown("""
    <style>

    .main{
        padding-top:1rem;
    }

    div[data-testid="stMetric"]{
        background:#d3d3d3 !important;
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
        font-size: 1.3rem;
        font-weight: 600;
    }
    div[data-testid="stMetricValue"] {
        color:#00c853 !important;
        font-weight:700 !important;
        text-shadow:0 1px 1px rgba(255, 255, 255, 0.7);
    }

    .metric-card {
        min-height:132px;
        background:#d3d3d3;
        border:1px solid #add8e6;
        padding:18px;
        border-radius:10px;
    }

    .metric-card .metric-label {
        color:#111827 !important;
        font-size:0.9rem;
        font-weight:600;
    }

    .metric-card .metric-value {
        color:#00c853 !important;
        font-size:2rem;
        font-weight:700;
        line-height:1.2;
        margin:8px 0;
        text-shadow:0 1px 1px rgba(255, 255, 255, 0.7);
    }

    .metric-card .metric-description {
        color:black !important;
        font-size:1.25rem;
        line-height:1.35;
    }
    </style>
    """, unsafe_allow_html=True)