import streamlit as st
import pandas as pd
import io

# 1. Konfigurasjon og Design
st.set_page_config(page_title="Solcelle-Analytikeren Pro", layout="centered")

# CSS for ekstrem overstyring av farger og mørk tekst i dropdowns
st.markdown("""
    <style>
    /* Hovedbakgrunn */
    .stApp {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }
    
    /* 1. OVERKRIFTER: Helt kritt-hvit */
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #ffffff !important;
        opacity: 1 !important;
        font-weight: 800 !important;
    }

    /* 2. BESKRIVELSER OG BRØDTEKST: Nesten helt hvit (#fafafa) */
    .stMarkdown p, .stMarkdown span, .stMarkdown div, .stMarkdown li, 
    label, p, span, div, .stCaption {
        color: #fafafa !important;
        opacity: 1 !important;
    }

    /* 3. SIDEBAR: Hvit bakgrunn med mørk tekst */
    section[data-testid="stSidebar"] {
        background-color: #f8fafc !important;
    }
    section[data-testid="stSidebar"] * {
        color: #1e293b !important;
    }

    /* 4. DROPDOWN/SELECTBOX: Tvinger teksten til å være sort */
    /* Dette fikser teksten inne i menyene i sidebaren */
    div[data-baseweb="select"] * {
        color: #000000 !important;
    }
    
    /* Fikser også fargen på selve input-feltene i sidebaren */
    div[data-testid="stSelectbox"] div {
        color: #000000 !important;
    }

    /* Avrunding av graf-beholderen */
    [data-testid="stArrowVegachart"] {
        border-radius: 7px !important;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }

    /* Metric-bokser */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 10px;
    }
    div[data-testid="stMetricValue"] {
        color: #ffcf33 !important;
    }

    /* Download-knappen */
    div.stDownloadButton > button {
        background-color: #ffcf33 !important;
        color: #000000 !important;
        font-weight: bold !important;
        border-radius: 7px !important;
        border: none !important;
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
region_kwh_map = {"Sør/Østlandet": 1000, "Vestlandet": 850, "Midt-Norge": 750, "Nord-Norge": 650}
region_effekt = region_kwh_map[region]

num_panels = int(area / 1.7)
system_kw = num_panels * 0.4
yearly_production = system_kw * region_effekt * dir_factor

cost_per_kw = 14000
total_investment = system_kw * cost_per_kw
enova_support = 7500 + (system_kw * 1250)
net_investment = total_investment - enova_support
annual_savings = yearly_production * el_price
payback_years = net_investment / annual_savings if annual_savings > 0 else 0

# --- VISNING ---
st.subheader("Hovedtall")
col1, col2 = st.columns(2)
with col1:
    st.metric("Årlig produksjon", f"{format_no(yearly_production)} kWh")
    st.metric("Antall paneler", f"{num_panels} stk")
with col2:
    st.metric("Netto investering", f"{format_no(net_investment)} kr")
    st.metric("Nedbetalingstid", f"{round(payback_years, 1)} år")

st.divider()
st.subheader("Akkumulert netto gevinst over 50 år (NOK)")

years = list(range(0, 51))
accumulated_values = [int(annual_savings * i - net_investment) for i in years]
df_graph = pd.DataFrame({"ÅR": years, "NOK": accumulated_values}).set_index("ÅR")
st.area_chart(df_graph)

# --- EXCEL ---
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    df_graph.reset_index().to_excel(writer, index=False, sheet_name='Nedbetalingsplan')
processed_data = output.getvalue()

st.download_button(
    label="📥 Last ned 50-års plan (Excel)",
    data=processed_data,
    file_name="solcelle_analyse_50aar.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.divider()
st.subheader("🌱 Din miljøprofil")
co2_saved_50y = (yearly_production * 50) * 0.4 / 1000
st.write(f"Over 50 år vil anlegget spare miljøet for ca. **{round(co2_saved_50y, 1)} tonn CO2**.")
