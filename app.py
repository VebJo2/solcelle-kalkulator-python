import streamlit as st
import pandas as pd
import io

# 1. Konfigurasjon og Design
st.set_page_config(page_title="Solcelle-Analytikeren Pro", layout="centered")

# Mørkt, profesjonelt tema med fadet bakgrunn
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        color: white;
    }
    div[data-testid="stMetricValue"] {
        color: #ffcf33;
    }
    .stHeader {
        color: #f8fafc;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("☀️ Solcelle-Analytikeren Pro")
st.write("Profesjonelt beslutningsverktøy for solenergi.")

# Hjelpefunksjon for tallformatering (1 000 000)
def format_no(number):
    return f"{int(number):,}".replace(",", " ")

# --- SIDEBAR: INNDATA ---
with st.sidebar:
    st.header("⚙️ Konfigurasjon")
    area = st.number_input("Takareal tilgjengelig (m2)", value=40, step=5)
    direction = st.selectbox("Takets retning", ["Sør (Optimalt)", "Øst/Vest", "Nord"])
    region = st.selectbox("Landsdel", ["Sør/Østlandet", "Vestlandet", "Midt-Norge", "Nord-Norge"])
    el_price = st.slider("Strømpris inkl. nettleie (NOK/kWh)", 0.5, 5.0, 1.5, step=0.1)

# --- LOGIKK OG BEREGNINGER ---
dir_factor = 1.0 if "Sør" in direction else 0.85 if "Øst" in direction else 0.6
region_kwh = {"Sør/Østlandet": 1000, "Vestlandet": 850, "Midt-Norge": 750, "Nord-Norge": 650}[region]

num_panels = int(area / 1.7)
system_kw = num_panels * 0.4
yearly_production = system_kw * region_kwh * dir_factor

# Økonomiske variabler
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

# --- GRAF OG DATA ---
st.divider()
st.subheader("Akkumulert netto gevinst (NOK)")

# Opprettelse av datasett for graf og Excel
years = list(range(0, 26))
accumulated_values = [int(annual_savings * i - net_investment) for i in years]

# Lag DataFrame med riktige kolonnenavn for grafen
df_graph = pd.DataFrame({
    "ÅR": years,
    "NOK": accumulated_values
}).set_index("ÅR")

st.area_chart(df_graph)

# --- EXCEL EKSPORT ---
# Opprett en Excel-fil i minnet ved hjelp av BytesIO
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    df_graph.reset_index().to_excel(writer, index=False, sheet_name='Nedbetalingsplan')
    # Her kan man legge til mer styling av Excel-arket om ønskelig
processed_data = output.getvalue()

st.download_button(
    label="📥 Last ned nedbetalingsplan (Excel)",
    data=processed_data,
    file_name="solcelle_analyse.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# --- MILJØPROFIL ---
st.divider()
st.subheader("🌱 Din miljøprofil")
co2_saved_25y = (yearly_production * 25) * 0.4 / 1000 # Basert på europeisk miks
st.write(f"Ditt anlegg vil spare miljøet for ca. **{round(co2_saved_25y, 1)} tonn CO2** over 25 år.")
st.caption("Dette tilsvarer CO2-opptaket til ca. " + str(int(co2_saved_25y * 50)) + " trær.")
