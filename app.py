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
    }

    /* Metric-bokser (Hovedtall) */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.03);
        padding: 15px;
        border-radius: 10px;
    }
    div[data-testid="stMetricValue"] {
        color: #ffcf33 !important;
        font-weight: 800;
    }

    /* Download-knappen: Gul med svart tekst */
    div.stDownloadButton > button {
        background-color: #ffcf33 !important;
        color: #000000 !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 7px !important;
        padding: 0.5rem 1rem !important;
    }
    div.stDownloadButton > button:hover {
        background-color: #e6b92d !important;
        color: #000000 !important;
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

    # Slider og manuelt felt koblet sammen
    el_price_slider = st.slider("Dra for å justere", 0.0, 10.0, float(st.session_state.price_input), step=0.1)
    el_price_manual = st.number_input("Eller skriv inn nøyaktig pris", value=float(el_price_slider), step=0.01)
    el_price = el_price_manual

# --- LOGIKK OG BEREGNINGER ---
dir_factor = 1.0 if "Sør" in direction else 0.85 if "Øst" in direction else 0.6
# Her var feilen - nå er den lukket korrekt:
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

# --- VISNING AV RESULTATER ---
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

df_graph = pd.DataFrame({
    "ÅR": years,
    "NOK": accumulated_values
}).set_index("ÅR")

# Grafen får avrundede hjørner via CSS-en i toppen
st.area_chart(df_graph)

# --- EXCEL EKSPORT ---
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    df_graph.reset_index().to_excel(writer, index=False, sheet_name='Nedbetalingsplan_50aar')
processed_data = output.getvalue()

st.download_button(
    label="📥 Last ned 50-års plan (Excel)",
    data=processed_data,
    file_name="solcelle_analyse_50aar.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# --- MILJØPROFIL ---
st.divider()
st.subheader("🌱 Din miljøprofil")
co2_saved_50y = (yearly_production * 50) * 0.4 / 1000
st.write(f"Over 50 år vil anlegget spare miljøet for ca. **{round(co2_saved_50y, 1)} tonn CO2**.")
st.caption("Dette tilsvarer CO2-opptaket til ca. " + str(int(co2_saved_50y * 50)) + " trær.")
