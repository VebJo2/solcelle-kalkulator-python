import streamlit as st
import pandas as pd
import io

# 1. Konfigurasjon og Design
st.set_page_config(page_title="Solcelle-Analytikeren Pro", layout="centered")

# Avansert CSS for farger og kontrast
st.markdown("""
    <style>
    /* Bakgrunn og hovedtekst */
    .stApp {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }
    
    /* Gjøre alle etiketter hvite */
    label, .stMarkdown p, h1, h2, h3 {
        color: #ffffff !important;
    }

    /* Spesifikk styling for Download-knappen (svart tekst) */
    div.stDownloadButton > button {
        background-color: #ffcf33 !important;
        color: #000000 !important;
        font-weight: bold !important;
        border: none !important;
        padding: 10px 20px !important;
    }
    
    div.stDownloadButton > button:hover {
        background-color: #e6b92d !important;
        color: #000000 !important;
    }

    /* Styling av metric-bokser for bedre synlighet */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("☀️ Solcelle-Analytikeren Pro")
st.write("Profesjonelt beslutningsverktøy for solenergi (0-50 år).")

def format_no(number):
    return f"{int(number):,}".replace(",", " ")

# --- SIDEBAR: INNDATA ---
with st.sidebar:
    st.header("⚙️ Konfigurasjon")
    area = st.number_input("Takareal tilgjengelig (m2)", value=40, step=5)
    direction = st.selectbox("Takets retning", ["Sør (Optimalt)", "Øst/Vest", "Nord"])
    region = st.selectbox("Landsdel", ["Sør/Østlandet", "Vestlandet", "Midt-Norge", "Nord-Norge"])
    
    st.write("---")
    st.write("**Strømpris inkl. nettleie (NOK/kWh)**")
    # Dobbel input-løsning: Slider + Manuelt felt
    if 'price_input' not in st.session_state:
        st.session_state.price_input = 1.5

    el_price_slider = st.slider("Dra for å justere", 0.0, 10.0, float
