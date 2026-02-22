import streamlit as st
import pandas as pd
import io

# 1. Konfigurasjon og Design
st.set_page_config(page_title="Solcelle-Analytikeren Pro", layout="centered")

# Avansert CSS for farger og kontrast
st.markdown("""
    <style>
    /* Hovedbakgrunn */
    .stApp {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }
    
    /* Hovedinnhold: Overskrifter og tekst i senter */
    .main h1, .main h2, .main h3, .main p, .main .stMarkdown {
        color: #ffffff !important;
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
    div[data-testid="metric-container"] label {
        color: #e2e8f0 !important; /* Lys grå/hvit tekst på merkelappen */
        font-weight: 500;
    }
    div[data-testid="stMetricValue"] {
        color: #ffcf33 !important; /* Gul farge på selve tallene */
        font-weight: 800;
    }

    /* Download-knappen */
    div.stDownloadButton > button {
        background-color: #ffcf33 !important;
        color: #000000 !important;
        font-weight: bold !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("☀️ Solcelle-Analytikeren Pro")
st.write("Profesjonelt beslutningsverktøy for solenergi.")

def format_no(number):
    return f"{int(number):,}".replace(",", " ")

# --- SIDEBAR: INNDATA (Mørk tekst her) ---
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
region_kwh = {"Sør/Østlandet": 1000, "Vestlandet": 850, "Midt-Norge": 750, "Nord-Norge": 650}[region]

num_panels = int(area / 1.7)
system_kw = num_panels * 0.4
yearly_production = system_kw * region_kwh * dir_factor

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
