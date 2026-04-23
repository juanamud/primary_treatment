import streamlit as st

st.set_page_config(page_title="PTAR Barbosa - Diseño", layout="wide", page_icon="🌊")

import bsm2_python.bsm2.init.asm1init_bsm2 as asm1init
import bsm2_python.bsm2.init.primclarinit_bsm2 as primclarinit
from bsm2_python.bsm2.primclar_bsm2 import PrimaryClarifier

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.title("🌊 PTAR Municipio de Barbosa, Antioquia")
st.markdown("### Simulación de Tratamiento Primario (Versión Estática)")

# --- 1. DATOS ESTÁTICOS DE BARBOSA ---
# ⚠️ REEMPLAZA ESTOS NÚMEROS CON LOS VALORES EXACTOS DE TU EXCEL ⚠️
escenarios_caudal = {
    "Año Actual - Caudal Medio Diario (Qmd)": 4500.0,
    "Año Actual - Caudal Máximo Horario (QMH)": 9200.0,
    "Año Proyección - Caudal Medio Diario (Qmd)": 6800.0,
    "Año Proyección - Caudal Máximo Horario (QMH)": 14000.0,
}

# --- 2. BARRA LATERAL: PARÁMETROS DE DISEÑO ---
st.sidebar.header("🔧 Escenarios de Diseño")
escenario_seleccionado = st.sidebar.selectbox(
    "Seleccionar Escenario de Proyección", list(escenarios_caudal.keys())
)
caudal_diseno = escenarios_caudal[escenario_seleccionado]

st.sidebar.metric("Caudal a simular (m³/d)", f"{caudal_diseno:,.1f}")

st.sidebar.subheader("Caracterización Fisicoquímica")
st.sidebar.write("*(Basado en datos preliminares de Barbosa)*")
# ⚠️ REEMPLAZA EL 250.0 CON EL VALOR REAL DE SST DE TU EXCEL ⚠️
ss_entrada = st.sidebar.number_input(
    "Sólidos Suspendidos (SST) (mg/L)", value=250.0, step=10.0, min_value=0.0
)

# Parámetro de diseño del tanque
vol_clarificador = st.sidebar.slider(
    "Volumen del Clarificador (m³)", min_value=500.0, max_value=5000.0, value=1500.0, step=100.0
)

# --- 3. LÓGICA DEL SIMULADOR BSM2 ---
# Inicializamos el Clarificador Primario
clarificador = PrimaryClarifier(
    vol_clarificador,
    primclarinit.YINIT1.copy(),
    primclarinit.PAR_P,
    asm1init.PAR1,
    primclarinit.XVECTOR_P,
    tempmodel=False,
    activate=False,
)

# Vector de entrada (Influyente)
input_vector = primclarinit.YINIT1.copy()
input_vector[14] = caudal_diseno  # Caudal Q
input_vector[13] = ss_entrada  # TSS

# Ejecutar simulación estática (1 paso de tiempo)
timestep_d = 1.0 / (24.0 * 60.0)  # 1 minuto
output_underflow, output_overflow, _ = clarificador.output(timestep_d, 0.0, input_vector)

# --- 4. RESULTADOS Y ANÁLISIS ---
st.header("📊 Comportamiento del Clarificador")

# Cálculos de resultados
tss_salida = output_overflow[13]
eficiencia = (1 - (tss_salida / ss_entrada)) * 100 if ss_entrada > 0 else float("nan")
caudal_lodos = output_underflow[14]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("TSS en Agua Clarificada", f"{tss_salida:.2f} mg/L")
    if ss_entrada > 0:
        st.caption(
            f"Remoción de SST: {eficiencia:.1f}% (respecto a {ss_entrada:.0f} mg/L en entrada). "
            "Agua que pasa al tratamiento secundario."
        )
    else:
        st.caption(
            "Indique SST de entrada mayor que 0 para calcular la remoción. "
            "Agua que pasa al tratamiento secundario."
        )

with col2:
    st.metric("Caudal de Lodos al Digestor", f"{caudal_lodos:.2f} m³/d")
    st.caption("Caudal por la tubería de fondo (Underflow)")

with col3:
    # Tiempo de retención hidráulica (TRH) en horas
    trh_horas = (vol_clarificador / caudal_diseno) * 24
    st.metric("Tiempo de Retención (TRH)", f"{trh_horas:.2f} h")
    st.caption("Idealmente entre 1.5 y 2.5 horas")

st.divider()
st.info(
    "💡 **Tip de Operación:** Cambia el escenario a 'Caudal Máximo Horario' o baja el volumen del "
    "clarificador en la barra lateral. Verás cómo el TRH cae, lo que significa que el agua pasa "
    "demasiado rápido y la eficiencia de sedimentación disminuye."
)
