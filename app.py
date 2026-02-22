import streamlit as st
import pandas as pd
import io

# 1. Konfigurasjon og Design
st.set_page_config(page_title="Solcelle-Analytikeren Pro", layout="centered")

# Avansert CSS for hierarki i lys tekst og avrundede grafer
st.markdown("""
    <style>
    /* Hovedbakgrunn */
    .stApp {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }
    
    /* Header-tekst (H1) - Den lyseste */
    .main h1 {
        color: #ffffff !important;
        font-weight: 800 !important;
    }

    /* Underoverskrifter og vanlig tekst - Litt mindre lys enn H1 */
    .main h2, .main h3, .main p, .main span, .main label {
        color: #f1f5f9 !important;
    }

    /* Avrunding av graf-beholderen */
    [data-testid="stArrowVegachart"] {
        border-radius: 7px !important;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Sidebar (Konfigurasjon): Mørk tekst på lys bakgrunn */
    section[data-testid="stSidebar"] {
        background-color: #f8fafc !important;
    }
    section[data-testid="stSidebar"] .stMarkdown p, 
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h1 {
        color: #1e293b !important;
    }

    /* Metric-bokser (Hovedtall) */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.03);
        padding: 15px;
        border-radius: 10px;
    }
    div[data-testid="stMetricValue"] {
        color: #ffcf33 !important; /* Gul farge på tallene for fokus */
        font-weight: 800;
    }

    /* Download-knappen */
    div.stDownloadButton > button {
        background-color: #ffcf33 !important;
        color: #000000 !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 7px !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("☀️ Solcelle-Analytikeren Pro")
st.write("Profesjonelt beslutningsverktøy for solenergi.")

def format_no(number):
    return f"{int(number):,}".replace(",", " ")

# --- SIDEBAR: INNDATA ---
with st.sidebar:
    st.header("⚙️ Konfigurasjon")
    area = st.number_input("Takareal tilgjengelig (m2)", value=40, step=5)
    direction = st.selectbox("Takets retning", ["Sør (Optimalt)", "Øst/Vest", "Nord"])
    region = st.selectbox("Landsdel", ["Sør/Østlandet", "Vestlandet", "Midt-Norge", "Nord-Norge"])
    
    st.write("---")
    st.write("Strømpris inkl. nettleie (NOK/kWh)")
    
    if 'price_input' not in st.session_state:
        st.session_state.price_input = 1.5

    el_price_slider = st.slider("Dra for å justere", 0.0, 10.0, float(st.session_state.price_input), step=0.1)
    el_price_manual = st.number_input("Eller skriv inn nøyaktig pris", value=float(el_price_slider), step=0.01)
    
    el_price = el_price_manual

# --- LOGIKK ---
dir_factor = 1.0 if "Sør" in direction else 0.85 if "Øst" in direction else 0.6
region_kwh = {"Sør/Østlandet": 1000, "Vestlandet": 850, "Midt-Norge": 750, "Nord-Norge": 650
