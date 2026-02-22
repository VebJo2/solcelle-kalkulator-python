import streamlit as st

st.set_page_config(page_title="Solcelle-Kalkulator", page_icon="☀️")

st.title("☀️ Solcelle-estimatoren (Python Edition)")
st.write("Dette er en profesjonell kalkulator for beregning av solenergipotensial.")

# Inputs i sidemenyen
with st.sidebar:
    st.header("Inndata")
    area = st.number_input("Takareal (m2)", value=40)
    direction = st.selectbox("Takets retning", ["Sør (Optimalt)", "Øst/Vest", "Nord"], index=0)
    region = st.selectbox("Landsdel", ["Sør/Østlandet", "Vestlandet", "Midt-Norge", "Nord-Norge"])

# Logikk
dir_factor = 1.0 if "Sør" in direction else 0.85 if "Øst" in direction else 0.6
region_kwh = {"Sør/Østlandet": 1000, "Vestlandet": 850, "Midt-Norge": 750, "Nord-Norge": 650}[region]

num_panels = int(area / 1.7)
system_kw = num_panels * 0.4
yearly_kwh = system_kw * region_kwh * dir_factor

# Økonomi
total_cost = system_kw * 14000
enova = 7500 + (system_kw * 1250)
final_price = total_cost - enova
annual_savings = yearly_kwh * 1.5
payback_years = final_price / annual_savings if annual_savings > 0 else 0

# Visning av resultater
col1, col2 = st.columns(2)
with col1:
    st.metric("Antall paneler", f"{num_panels} stk")
    st.metric("Årlig produksjon", f"{int(yearly_kwh)} kWh")

with col2:
    st.metric("Estimert pris (etter Enova)", f"{int(final_price)} kr")
    st.metric("Nedbetalingstid", f"{round(payback_years, 1)} år")

if st.button("Vis detaljert nedbetalingsplan"):
    st.write("### Akkumulert besparelse over 25 år")
    plan = [int(annual_savings * i - final_price) for i in range(1, 26)]
    st.line_chart(plan)
