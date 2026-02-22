import streamlit as st
import pandas as pd
import io

# 1. Konfigurasjon og Design
st.set_page_config(page_title="Solcelle-Analytikeren Pro", layout="centered")

# CSS for hierarki, avrunding og farger
st.markdown("""
    <style>
    /* Hovedbakgrunn */
    .stApp {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }
    
    /* Header-tekst (H1) - Den aller lyseste */
    .main h1 {
        color: #ffffff !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }

    /* Underoverskrifter og vanlig tekst - Ørlite grann mørkere enn H1 (#f1f5f9) */
    .main h2, .main h3, .main p, .main span, .main label {
        color: #f1f5f9 !important;
    }

    /* Avrunding av graf-beholderen (7px border radius) */
    [data-testid="stArrowVegachart"] {
        border-radius: 7px !important;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.1);
        background-color: rgba(255, 255, 255, 0.02);
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
