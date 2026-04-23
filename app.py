import streamlit as st
import pandas as pd
import numpy as np

# --- 1. CONFIGURACIÓN E INTERFAZ ---
st.set_page_config(
    page_title="Diseño PTAR Barbosa - Lagunas",
    layout="wide",
    page_icon="🏗️",
)

st.title("🏗️ Sistema de Diseño de Lagunas de Estabilización")
st.markdown("### Proyecto: Municipio de Barbosa, Antioquia")

# --- 2. DATOS DE ENTRADA (BARBOSA EXCEL) ---
st.sidebar.header("📥 Datos Maestros")
caudal = st.sidebar.number_input("Caudal de Diseño (Q) [m³/d]", value=5200.0, step=100.0)
dbo_in = st.sidebar.number_input("DBO₅ de Entrada [mg/L]", value=280.0, step=10.0)
dqo_in = st.sidebar.number_input("DQO de Entrada [mg/L]", value=450.0, step=10.0)
coliformes_in = st.sidebar.number_input("Coliformes [NMP/100ml]", value=1.0e7, format="%.1e")
temp = st.sidebar.slider("Temperatura del Agua (°C)", 15, 30, 22)

# --- 3. LÓGICA DE INGENIERÍA (PDF CLASE 09 Y EJERCICIO) ---
# Constante Kb ajustada por temperatura (Kb20 = 2.6 y theta = 1.19 del ejercicio)
kb_t = 2.6 * (1.19 ** (temp - 20))

# Pestañas para organizar el diseño
tab1, tab2, tab3, tab4 = st.tabs([
    "📍 Fase Anaerobia", "📍 Fase Facultativa", "📍 Fase Maduración", "📊 Resumen Ejecutivo"
])

with tab1:
    st.header("1. Laguna Anaerobia (Primario)")
    st.info("Diseño por Carga Orgánica Volumétrica (λv)")
    
    col1, col2 = st.columns(2)
    with col1:
        carga_v = st.number_input("Carga Volumétrica Adm. [g/m³·d]", value=200)
        prof_ana = st.slider("Profundidad (H) [m]", 3.0, 5.0, 4.0)
    
    # Cálculos
    vol_ana = (caudal * dqo_in) / carga_v
    trh_ana = vol_ana / caudal
    dbo_out_ana = dbo_in * 0.5 # Eficiencia del 50% según Clase 09
    
    with col2:
        st.metric("Volumen Requerido", f"{vol_ana:,.1f} m³")
        st.metric("TRH Resultante", f"{trh_ana:.2f} días")
        st.caption(f"Área necesaria: {vol_ana/prof_ana:,.1f} m²")

with tab2:
    st.header("2. Laguna Facultativa (Secundario)")
    st.info("Diseño por Carga Superficial (λs)")
    
    col1, col2 = st.columns(2)
    with col1:
        carga_s = 10 * temp + 50 # Fórmula RAS / Clase 09
        prof_fac = st.slider("Profundidad Útil [m]", 1.5, 2.5, 1.8)
    
    # Área en hectáreas
    area_fac_ha = (caudal * dbo_out_ana / 1000) / carga_s
    vol_fac = area_fac_ha * 10000 * prof_fac
    trh_fac = vol_fac / caudal
    dbo_out_fac = dbo_out_ana * 0.4 # 60% remoción de esta etapa
    
    with col2:
        st.metric("Área Requerida", f"{area_fac_ha:.2f} Ha")
        st.metric("TRH Facultativo", f"{trh_fac:.2f} días")

with tab3:
    st.header("3. Lagunas de Maduración (Terciario)")
    st.write("Cálculo de remoción de patógenos (Modelo en serie del Ejercicio)")
    
    n_lag = st.sidebar.number_input("N° de lagunas en serie", value=3, min_value=1)
    trh_mad_total = st.sidebar.slider("TRH maduración total (días)", 5, 20, 10)
    t_mad = trh_mad_total / n_lag
    
    # Fórmula de remoción bacteriana del PDF
    divisor = (1 + kb_t * trh_ana) * (1 + kb_t * trh_fac) * ((1 + kb_t * t_mad)**n_lag)
    coliformes_out = coliformes_in / divisor
    
    c1, c2 = st.columns(2)
    c1.metric("Coliformes Salida", f"{coliformes_out:.2e}")
    if coliformes_out < 1000:
        c2.success("Cumple norma de riego")
    else:
        c2.warning("Requiere más tiempo de retención")

with tab4:
    st.header("📈 Resumen de Eficiencia - PTAR Barbosa")
    
    # Datos para el gráfico
    resumen_data = pd.DataFrame({
        "Etapa": ["Entrada", "Anaerobia", "Facultativa", "Salida"],
        "DBO₅ [mg/L]": [dbo_in, dbo_out_ana, dbo_out_fac, dbo_out_fac*0.8]
    })
    st.bar_chart(resumen_data.set_index("Etapa"))
    
    st.subheader("📋 Memoria de Cálculo")
    memoria = pd.DataFrame({
        "Unidad": ["Anaerobia", "Facultativa", f"Maduración (x{n_lag})"],
        "Volumen (m³)": [f"{vol_ana:.0f}", f"{vol_fac:.0f}", f"{(caudal*t_mad):.0f}"],
        "TRH (días)": [f"{trh_ana:.2f}", f"{trh_fac:.2f}", f"{t_mad:.2f}"]
    })
    st.table(memoria)