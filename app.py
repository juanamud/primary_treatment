import streamlit as st

st.set_page_config(
    page_title="Diseño PTAR Barbosa - Lagunas",
    layout="wide",
    page_icon="🏗️",
)

import pandas as pd
import plotly.graph_objects as go

st.title("🏗️ Sistema de Tratamiento por Lagunas de Estabilización")
st.markdown("### Proyecto: Municipio de Barbosa, Antioquia")

# --- SIDEBAR: DATOS MAESTROS (CARACTERIZACIÓN EXCEL) ---
st.sidebar.header("📥 Datos de Entrada (Barbosa)")
caudal_diseno = st.sidebar.number_input(
    "Caudal de Diseño (Q) [m³/d]", value=5200.0, min_value=0.0, step=100.0
)
dbo_entrada = st.sidebar.number_input(
    "DBO₅ de Entrada [mg/L]", value=280.0, min_value=0.0, step=10.0
)
coliformes_in = st.sidebar.number_input(
    "Coliformes Fecales [NMP/100ml]", value=1.0e7, min_value=0.0, format="%.1e"
)
temp_agua = st.sidebar.slider("Temperatura del Agua (°C)", 15, 30, 22)

if caudal_diseno <= 0:
    st.warning("Indica un **caudal de diseño mayor que 0** m³/d para TRH y áreas coherentes.")

# --- CÁLCULO DE CONSTANTE DE DECAIMIENTO (K) ---
# Según el ejercicio: Kb(T) = Kb(20) * theta^(T-20)
kb_20 = 2.6  # Dato del ejercicio resuelto
theta = 1.19  # Factor de ajuste
kb_t = kb_20 * (theta ** (temp_agua - 20))

# --- PESTAÑAS DE DISEÑO ---
tab1, tab2, tab3, tab4 = st.tabs(
    ["Laguna Anaerobia", "Laguna Facultativa", "Lagunas de Maduración", "Resumen de Eficiencia"]
)

with tab1:
    st.header("1️⃣ Fase Primaria: Laguna Anaerobia")
    st.info("Objetivo: Remoción de carga orgánica pesada y sólidos por sedimentación y digestión.")

    col1, col2 = st.columns(2)
    with col1:
        carga_v_adm = st.number_input(
            "Carga Orgánica Volumétrica Adm. [g/m³·d]", value=200, min_value=1.0, step=10.0
        )
        prof_ana = st.slider("Profundidad Laguna Anaerobia [m]", 3.0, 5.0, 4.0)

    if caudal_diseno > 0 and carga_v_adm > 0 and prof_ana > 0:
        vol_ana = (caudal_diseno * dbo_entrada) / carga_v_adm
        area_ana = vol_ana / prof_ana
        trh_ana = vol_ana / caudal_diseno
    else:
        vol_ana = area_ana = trh_ana = 0.0

    # Eficiencia (Normalmente 50-60% según Clase 09)
    eficiencia_ana = 0.50
    dbo_salida_ana = dbo_entrada * (1 - eficiencia_ana)

    with col2:
        st.metric("Volumen Requerido", f"{vol_ana:,.2f} m³")
        st.metric("TRH Anaerobia", f"{trh_ana:.2f} días")
        st.metric("DBO₅ Salida", f"{dbo_salida_ana:.2f} mg/L")
        if area_ana > 0:
            st.caption(f"Área superficial aprox.: {area_ana:,.0f} m²")

with tab2:
    st.header("2️⃣ Fase Secundaria: Laguna Facultativa")
    st.info("Objetivo: Remoción de DBO remanente mediante simbiosis Algas-Bacterias.")

    col1, col2 = st.columns(2)
    with col1:
        # Carga superficial recomendada según Clase 09 (promedio)
        carga_s_adm = 10 * temp_agua + 50
        prof_fac = st.slider("Profundidad Laguna Facultativa [m]", 1.5, 2.5, 1.8)

    if caudal_diseno > 0 and carga_s_adm > 0:
        area_fac_ha = (caudal_diseno * dbo_salida_ana / 1000) / carga_s_adm
        area_fac_m2 = area_fac_ha * 10000
        vol_fac = area_fac_m2 * prof_fac
        trh_fac = vol_fac / caudal_diseno
    else:
        area_fac_ha = area_fac_m2 = vol_fac = trh_fac = 0.0

    # Eficiencia acumulada (Suele bajar a un total de 80% del inicial)
    dbo_salida_fac = dbo_salida_ana * 0.4  # Remoción del 60% de lo que entró

    with col2:
        st.metric("Área Facultativa", f"{area_fac_ha:.2f} Ha")
        st.metric("TRH Facultativo", f"{trh_fac:.2f} días")
        st.metric("DBO₅ Salida", f"{dbo_salida_fac:.2f} mg/L")

with tab3:
    st.header("3️⃣ Fase Terciaria: Lagunas de Maduración")
    st.write("Cálculo basado en el **Modelo de Mezcla Completa en Serie** del ejercicio resuelto.")

    col1, col2 = st.columns(2)
    with col1:
        n_lagunas = st.number_input("Número de lagunas en serie", value=3, min_value=1, step=1)
        trh_mad_total = st.slider("TRH total de maduración [días]", 5, 20, 10)
        trh_por_laguna = trh_mad_total / n_lagunas

    # Fórmula del ejercicio resuelto:
    # Ne = Ni / [ (1+Kb*t_ana) * (1+Kb*t_fac) * (1+Kb*t_mad)^n ]
    divisor = (1 + kb_t * trh_ana) * (1 + kb_t * trh_fac) * ((1 + kb_t * trh_por_laguna) ** n_lagunas)
    if divisor > 0 and coliformes_in >= 0:
        coliformes_out = coliformes_in / divisor
    else:
        coliformes_out = float("nan")

    with col2:
        if coliformes_in <= 0:
            st.metric("Coliformes Salida", "—")
            st.caption("Indique una concentración de entrada > 0 para estimar la salida.")
        else:
            st.metric("Coliformes Salida", f"{coliformes_out:.2e} NMP/100ml")
        st.write(f"Constante Kb usada: **{kb_t:.3f} d⁻¹**")

        if coliformes_in > 0 and coliformes_out == coliformes_out:  # not NaN
            if coliformes_out < 1000:
                st.success("✅ Cumple Clase A (Riego sin restricciones)")
            else:
                st.warning("⚠️ Requiere más días o más lagunas para contacto primario")

with tab4:
    st.header("📈 Resumen del Tren de Tratamiento")

    # Gráfico de barras de remoción de DBO
    etapas = ["Crudo (Entrada)", "Anaerobia", "Facultativa", "Maduración"]
    valores_dbo = [dbo_entrada, dbo_salida_ana, dbo_salida_fac, dbo_salida_fac * 0.8]

    fig = go.Figure(
        data=[go.Bar(name="DBO₅ (mg/L)", x=etapas, y=valores_dbo, marker_color="#2E8B57")]
    )
    fig.update_layout(title_text="Perfil de Remoción de Materia Orgánica")
    st.plotly_chart(fig, width="stretch")

    # Memoria de diseño rápida
    st.subheader("📋 Dimensiones Generales")
    df_resumen = pd.DataFrame(
        {
            "Unidad": ["Anaerobia", "Facultativa", f"Maduración (x{n_lagunas})"],
            "TRH (d)": [f"{trh_ana:.2f}", f"{trh_fac:.2f}", f"{trh_por_laguna:.2f}"],
            "Volumen (m³)": [
                f"{vol_ana:.0f}",
                f"{vol_fac:.0f}",
                f"{(caudal_diseno * trh_por_laguna):.0f}",
            ],
        }
    )
    st.table(df_resumen)
