import streamlit as st

st.set_page_config(page_title="Diseño PTAR Barbosa", layout="wide", page_icon="📐")

st.title("📐 Dimensionamiento de Laguna Anaerobia Primaria")
st.subheader("Proyecto: Municipio de Barbosa, Antioquia")

# --- 1. DATOS DE ENTRADA (De tu Excel) ---
with st.expander("📥 Datos de Caracterización y Caudal", expanded=True):
    col_a, col_b = st.columns(2)
    with col_a:
        # Aquí irían los datos fijos que sacaste del Excel
        caudal_m3_dia = st.number_input(
            "Caudal de Diseño (Q) [m³/día]", value=5200.0, min_value=0.0, step=100.0
        )
        dqo_entrada = st.number_input(
            "DQO de entrada (S0) [mg/L]", value=480.0, min_value=0.0, step=10.0
        )
    with col_b:
        temp_ambiente = st.slider("Temperatura promedio (°C)", 15, 30, 22)

# --- 2. CRITERIOS DE DISEÑO (Parámetros del Profesor/RAS) ---
st.sidebar.header("⚙️ Criterios de Diseño")
# El RAS recomienda entre 100 y 300 g/m3*d para lagunas anaerobias
carga_diseno = st.sidebar.select_slider(
    "Carga Orgánica Volumétrica (λv) [g/m³·d]",
    options=[100, 150, 200, 250, 300],
    value=200,
)
profundidad_diseno = st.sidebar.slider("Profundidad Útil (H) [m]", 2.5, 5.0, 3.5)
relacion_lw = st.sidebar.slider("Relación Largo:Ancho (L:W)", 1.0, 4.0, 2.0)

# --- 3. CÁLCULOS DE INGENIERÍA ---
if caudal_m3_dia > 0 and carga_diseno > 0 and profundidad_diseno > 0:
    # Volumen requerido (V = Q * S0 / λv)
    # Nota: mg/L y g/m³ son equivalentes en este contexto
    volumen_req = (caudal_m3_dia * dqo_entrada) / carga_diseno
    area_req = volumen_req / profundidad_diseno
    ancho = (area_req / relacion_lw) ** 0.5
    largo = ancho * relacion_lw
    trh_dias = volumen_req / caudal_m3_dia
else:
    volumen_req = area_req = ancho = largo = trh_dias = 0.0

# --- 4. PRESENTACIÓN DEL DISEÑO ---
st.header("📋 Memoria de Cálculo")
st.caption(
    f"Condiciones de partida: Q = {caudal_m3_dia:,.0f} m³/d · S0 = {dqo_entrada:.0f} mg/L · "
    f"T ≈ {temp_ambiente} °C (referencia para criterios de operación y textos de memoria)."
)

res1, res2, res3 = st.columns(3)
res1.metric("Volumen Total", f"{volumen_req:,.2f} m³")
res2.metric("Área Requerida", f"{area_req:,.2f} m²")
res3.metric("TRH Resultante", f"{trh_dias:.2f} días")

st.subheader("📐 Dimensiones Finales")
d1, d2, d3 = st.columns(3)
d1.write(f"**Ancho (W):** {ancho:.2f} m")
d2.write(f"**Largo (L):** {largo:.2f} m")
d3.write(f"**Profundidad (H):** {profundidad_diseno:.2f} m")

# --- 5. VALIDACIÓN TÉCNICA ---
st.divider()
if caudal_m3_dia <= 0:
    st.warning("Indica un caudal de diseño mayor que 0 para obtener dimensiones y TRH.")
elif 1.0 <= trh_dias <= 5.0:
    st.success("✅ El TRH cumple con los rangos típicos para lagunas anaerobias primarias (1-5 días).")
else:
    st.error("⚠️ El TRH está fuera de rango. Ajusta la carga de diseño o la profundidad.")

# Representación visual simple (escala en pantalla, proporción L:W real)
st.write("**Vista en Planta (Esquema):**")
if largo > 0 and ancho > 0:
    max_px = 420
    escala = max_px / max(largo, ancho)
    w_px = max(40, int(largo * escala))
    h_px = max(40, int(ancho * escala))
    st.markdown(
        f"""
<div style="width:{w_px}px; height:{h_px}px; background-color:#4e6e5d; border:2px solid #ccc;
  display:flex; align-items:center; justify-content:center; color:white; font-size:14px;">
    {largo:.1f} m × {ancho:.1f} m
</div>
""",
        unsafe_allow_html=True,
    )
else:
    st.caption("El esquema aparecerá cuando el caudal y los criterios permitan calcular dimensiones.")
