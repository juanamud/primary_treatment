# 💧 Diseño de PTAR - Caso Barbosa, Antioquia

Aplicación web local desarrollada en **Python + Streamlit** para diseñar plantas de tratamiento de aguas residuales (PTAR) con tres alternativas de tratamiento primario, comparación con lodos activados y postratamiento por lagunas.

> Proyecto académico para la materia **Sistemas de Tratamiento de Aguas Residuales** del programa de Ingeniería Sanitaria, Universidad de Antioquia.

---

## 🏗️ Tren de tratamiento

```
Afluente → [Primario] → [Secundario] → [Terciario] → Vertimiento/Reúso

Tres alternativas para el primario:
  ├── 🏛️ Sedimentador 1° (Qasim, RAS 2017)
  ├── 🌊 Laguna Anaerobia (Mara 1997)
  └── ⚗️ Reactor UASB (van Haandel & Lettinga 1994)

Dos alternativas para secundario+terciario:
  ├── 🌱 Lagunas Facultativa + Maduración (extensivo)
  └── ⚙️ Lodos Activados + Sedimentador 2° + Cloración (intensivo)
```

## 📂 Estructura del proyecto

```
proyecto/
├── app.py              # Interfaz Streamlit + planos esquemáticos
├── diseno.py           # Funciones de ingeniería (testeables)
├── test_diseno.py      # Suite de pruebas pytest (57 tests)
├── requirements.txt    # Dependencias
└── README.md           # Este archivo
```

La separación entre `app.py` (UI) y `diseno.py` (cálculo) permite ejecutar la suite de pruebas automatizada sin necesidad de Streamlit.

## ⚙️ Funcionalidades

### Diseño y dimensionamiento
- Proyección poblacional geométrica + caudales Qmd, QMD, QMH (RAS 2017)
- Selección automática del primario según área disponible
- Cálculo de volúmenes, áreas, dimensiones físicas (L × W × H, talud, diámetro)
- Régimen hidráulico seleccionable: mezcla completa, flujo pistón, flujo disperso (Wehner-Wilhelm)
- Unidades en paralelo configurables por tipo
- Verificación con QMH para velocidad ascensional UASB

### Planos esquemáticos con simbología técnica
- Vista en planta + corte transversal/longitudinal por unidad
- Norte, escala gráfica, leyenda, cuadro de información
- Cota de referencia (NA, solera)
- Talud configurable (1:m) con representación correcta
- **Layout de planta** con todas las unidades en el lote disponible

### Análisis adicional
- **Manejo de lodos**: volumen anual, frecuencia de evacuación, área de lechos de secado
- **Comparador**: tren de lagunas vs tren de lodos activados (área, energía, costos)
- **Cumplimiento normativo**: Resolución 0631 de 2015, Decreto 1076 de 2015 (reúso)
- **Análisis de sensibilidad** ante temperatura
- **Costos US$/hab** según rangos de von Sperling & Chernicharo (Clase 09)
- **Aprovechamiento energético del biogás**: kWh, MWh/año
- **Tabla de operación y mantenimiento** por unidad con frecuencias y acciones

### Exportación
- Memoria de cálculo descargable en Word (.docx) con esquemas embebidos
- Suite de pruebas automatizadas (`pytest`) con 57 tests

## 📋 Requisitos

- Python 3.9 o superior
- Dependencias en `requirements.txt`:
  ```
  streamlit, pandas, numpy, matplotlib, python-docx, pytest
  ```

## 🚀 Instalación y uso

```bash
# Clonar
git clone https://github.com/<tu-usuario>/ptar-barbosa.git
cd ptar-barbosa

# Entorno virtual
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar
pip install -r requirements.txt

# Ejecutar la aplicación
streamlit run app.py

# Correr la suite de pruebas
pytest test_diseno.py -v
```

La app abre en `http://localhost:8501`.

## 🧭 Estructura de pestañas (13)

| Pestaña | Contenido |
|---|---|
| 📍 Caudales | Proyección poblacional + Qmd/QMD/QMH |
| 📐 Selección + Costos | Comparación 3 alternativas + recomendación + costos |
| 🏛️ Sedimentador | Diseño RAS Art. 189 + plano |
| 🌊 Anaerobia | Diseño Mara + plano con talud |
| ⚗️ UASB | Diseño + biogás + energía + plano |
| 🌱 Facultativa | Diseño con régimen hidráulico + plano |
| 💧 Maduración | Lagunas en serie + cinética coliformes + plano |
| 🪣 Lodos | Gestión completa de lodos del tren |
| 🗺️ Layout | Plano de implantación de toda la PTAR en el lote |
| ⚙️ Lodos Activados | Tren alternativo + comparador con lagunas |
| 🛠️ O&M | Tabla de operación y mantenimiento por unidad |
| 📈 Sensibilidad | Análisis ante temperatura |
| 📊 Resumen | Tren completo + cumplimiento Res 0631 + exportación Word |

## 🔬 Validación

Las **57 pruebas automatizadas** validan que las fórmulas reproducen exactamente:

- Tabla de Mara (1997) para Lv anaerobia y eficiencia DBO según T
- Ejemplo completo de laguna facultativa del PDF Clase 09 (DBO efluente 38 mg/L, k 0,41 d⁻¹, eficiencia 81%)
- Balance de DQO del UASB del PDF Clase UASB (300 kg/d → 247,35 kg DQO al CH₄)
- Acumulación de lodos del PDF (3 cm/año para 20.000 hab y 33.800 m²)
- Comportamiento intermedio de flujo disperso entre pistón y mezcla completa
- Lógica de recomendación según área disponible

```bash
$ pytest test_diseno.py -v
============================== 57 passed in 0.04s ==============================
```

## 📚 Referencias bibliográficas

- Mara, D. D. (1997). *Design manual for waste stabilization ponds in India*.
- Von Sperling, M. y Lemos Chernicharo, C. A. (2005). *Biological wastewater treatment in warm climate regions*. IWA.
- Van Haandel, A. C. y Lettinga, G. (1994). *Tratamento anaeróbio de esgotos*.
- Qasim, S. R. (1999). *Wastewater Treatment Plants*.
- Metcalf & Eddy (2014). *Wastewater Engineering* (lodos activados).
- Colombia. RAS - Resolución 0330 de 2017.
- Colombia. Resolución 0631 de 2015 - límites de vertimientos.
- Molina Pérez, F. (2020-2024). Apuntes de clase, UdeA.

## 📌 Caso de estudio: Barbosa, Antioquia

| Parámetro | Valor |
|---|---|
| Población actual | 55.000 hab |
| Población diseño (25 años, r=1,4%) | ~78.000 hab |
| Dotación neta | 130 L/hab·d |
| DBO₅ / DQO / SST afluente | 280 / 450 / 220 mg/L |
| Coliformes fecales | 1,5 × 10⁷ NMP/100mL |
| Temperatura aire (mes frío) | 19 °C |
| Área disponible | 60.000 m² |

## 👤 Autor

Juan Amud · Ingeniería Sanitaria · Universidad de Antioquia
