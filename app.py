import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Diseño PTAR Barbosa", layout="wide")
st.title("📐 Dimensionamiento de Laguna Anaerobia Primaria")
st.subheader("Proyecto: Municipio de Barbosa, Antioquia")

# --- 1. DATOS DE ENTRADA (De tu Excel) ---
with st.expander("📥 Datos de Caracterización y Caudal", expanded=True):
    col_a, col_b = st.columns(2)
    with col_a:
        # Aquí irían los datos fijos que sacaste del Excel
        caudal_m3_dia = st.number_input("Caudal de Diseño (Q) [m³/día]", value=5200.0)
        dqo_entrada = st.number_input("DQO de entrada (S0) [mg/L]", value=480.0)
    with col_b:
        temp_ambiente = st.slider("Temperatura promedio (°C)", 15, 30, 22)

# --- 2. CRITERIOS DE DISEÑO (Parámetros del Profesor/RAS) ---
st.sidebar.header("⚙️ Criterios de Diseño")
# El RAS recomienda entre 100 y 300 g/m3*d para lagunas anaerobias
carga_diseno = st.sidebar.select_slider(
    "Carga Orgánica Volumétrica (λv) [g/m³·d]",
    options=[100, 150, 200, 250, 300],
    value=200
)
profundidad_diseno = st.sidebar.slider("Profundidad Útil (H) [m]", 2.5, 5.0, 3.5)
relacion_lw = st.sidebar.slider("Relación Largo:Ancho (L:W)", 1.0, 4.0, 2.0)

# --- 3. CÁLCULOS DE INGENIERÍA ---
# Volumen requerido (V = Q * S0 / λv)
# Nota: Convertimos mg/L a g/m3 (es 1 a 1)
volumen_req = (caudal_m3_dia * dqo_entrada) / carga_diseno

# Área superficial
area_req = volumen_req / profundidad_diseno

# Dimensiones en planta (A = L * W  => A = (rel * W) * W => W = sqrt(A/rel))
ancho = (area_req / relacion_lw)**0.5
largo = ancho * relacion_lw

# Tiempo de Retención Hidráulica (TRH)
trh_dias = volumen_req / caudal_m3_dia

# --- 4. PRESENTACIÓN DEL DISEÑO ---
st.header("📋 Memoria de Cálculo")

res1, res2, res3 = st.columns(3)
res1.metric("Volumen Total", f"{volumen_req:.2f} m³")
res2.metric("Área Requerida", f"{area_req:.2f} m²")
res3.metric("TRH Resultante", f"{trh_dias:.2f} días")

st.subheader("📐 Dimensiones Finales")
d1, d2, d3 = st.columns(3)
d1.write(f"**Ancho (W):** {ancho:.2f} m")
d2.write(f"**Largo (L):** {largo:.2f} m")
d3.write(f"**Profundidad (H):** {profundidad_diseno:.2f} m")

# --- 5. VALIDACIÓN TÉCNICA ---
st.divider()
if 1.0 <= trh_dias <= 5.0:
    st.success("✅ El TRH cumple con los rangos típicos para lagunas anaerobias primarias (1-5 días).")
else:
    st.error("⚠️ El TRH está fuera de rango. Ajusta la carga de diseño o la profundidad.")

# Representación visual simple
st.write("**Vista en Planta (Esquema):**")
st.markdown(f"""
<div style="width:{largo*2}px; height:{ancho*2}px; background-color:#4e6e5d; border:2px solid white; display:flex; align-items:center; justify-content:center; color:white;">
    {largo:.1f}m x {ancho:.1f}m
</div>
""", unsafe_url_allowed=True)