import streamlit as st
import pandas as pd

import bsm2_python.bsm2.init.asm1init_bsm2 as asm1init
import bsm2_python.bsm2.init.primclarinit_bsm2 as primclarinit
from bsm2_python.bsm2.primclar_bsm2 import PrimaryClarifier

# --- INTERFAZ DE STREAMLIT ---
st.set_page_config(page_title="PTAR Antioquia - Tratamiento Primario", layout="wide")

st.title("🌊 Simulador de Tratamiento Primario")
st.markdown("### Caso de Estudio: Municipio en Antioquia")

# Sidebar para configurar el municipio
municipio = st.sidebar.selectbox("Selecciona el Municipio", ["Medellín (San Fernando/Aguas Claras)", "Rionegro", "Marinilla", "Otro (Personalizado)"])

# Ajuste de parámetros según el municipio (valores estimados para el ejemplo)
if municipio == "Medellín (San Fernando/Aguas Claras)":
    q_default, tss_default = 15000.0, 300.0
else:
    q_default, tss_default = 2500.0, 220.0

st.sidebar.header("Parámetros de Entrada")
caudal = st.sidebar.slider("Caudal de entrada (m³/d)", 500.0, 50000.0, q_default)
ss_entrada = st.sidebar.slider("Sólidos Suspendidos (mg/L)", 50.0, 500.0, tss_default)

# --- LÓGICA CON BSM2-PYTHON ---
# 1. Clarificador (API BSM2: volumen, estado inicial, parámetros del módulo y ASM1)
clarificador = PrimaryClarifier(
    1500.0,
    primclarinit.YINIT1.copy(),
    primclarinit.PAR_P,
    asm1init.PAR1,
    primclarinit.XVECTOR_P,
    tempmodel=False,
    activate=False,
)

# 2. Influent (21 estados): perfil BSM2 con caudal (Q=14) y TSS (13) del usuario
input_vector = primclarinit.YINIT1.copy()
input_vector[14] = caudal
input_vector[13] = ss_entrada

# 3. Un paso de tiempo (1 min en días, como en el layout BSM2 por defecto)
timestep_d = 1.0 / (24.0 * 60.0)
output_underflow, output_overflow, _ = clarificador.output(timestep_d, 0.0, input_vector)

# --- VISUALIZACIÓN DE RESULTADOS ---
st.header(f"📊 Resultados para {municipio}")

col1, col2 = st.columns(2)

with col1:
    st.metric("Sólidos en Agua Clarificada", f"{output_overflow[13]:.2f} mg/L")
    eficiencia = (1 - (output_overflow[13] / ss_entrada)) * 100
    st.write(f"**Eficiencia de remoción:** {eficiencia:.1f}%")

with col2:
    st.metric("Lodo Primario Producido", f"{output_underflow[14]:.2f} m³/d")
    st.write("Este lodo tiene una alta concentración de sólidos y debe ir a digestión anaerobia.")

# Gráfico comparativo
data = pd.DataFrame({
    'Ubicación': ['Entrada (Crudo)', 'Salida (Clarificada)'],
    'Sólidos (mg/L)': [ss_entrada, output_overflow[13]]
})
st.bar_chart(data.set_index('Ubicación'))