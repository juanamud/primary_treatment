# 💧 Diseño de PTAR - Caso Barbosa, Antioquia

Aplicación web local desarrollada en **Python + Streamlit** para diseñar plantas de tratamiento de aguas residuales (PTAR) con tres alternativas de tratamiento primario y postratamiento secundario y terciario por lagunas.

> Proyecto académico para la materia **Sistemas de Tratamiento de Aguas Residuales** del programa de Ingeniería Sanitaria, Universidad de Antioquia.

---

## 🎯 Objetivo

Diseñar y comparar tres alternativas de tratamiento primario para las aguas residuales del municipio de Barbosa, Antioquia, con su correspondiente postratamiento por lagunas facultativas y de maduración. La herramienta calcula volúmenes, áreas, dimensiones físicas, eficiencias de remoción, manejo de lodos, costos comparativos, cumplimiento normativo y producción energética del biogás (UASB).

## 🏗️ Tren de tratamiento

```
Afluente → [Primario] → Laguna Facultativa → Lagunas de Maduración → Vertimiento/Reúso

Tres alternativas para el primario:
  ├── 🏛️ Sedimentador 1° (Qasim, RAS 2017)
  ├── 🌊 Laguna Anaerobia (Mara 1997)
  └── ⚗️ Reactor UASB (van Haandel & Lettinga 1994)
```

La aplicación recomienda la mejor alternativa primaria según el área disponible.

## ⚙️ Funcionalidades

- **Proyección poblacional geométrica** y cálculo de Qmd, QMD, QMH (RAS 2017)
- **Selección automática** del tratamiento primario según área disponible
- **Planos esquemáticos** (planta + corte) con dimensiones para cada unidad
- **Diagrama del tren completo** con concentraciones por etapa
- **Manejo de lodos**: volumen anual, frecuencia de evacuación, área de lechos de secado
- **Cumplimiento normativo** Resolución 0631 de 2015 (Colombia)
- **Análisis de sensibilidad** ante temperatura y carga orgánica
- **Costos comparativos** US$/hab según rangos de von Sperling & Chernicharo
- **Verificación con QMH** para velocidad ascensional en UASB
- **Unidades en paralelo** configurables por unidad (1-6)
- **Aprovechamiento energético** del biogás (kWh, MWh/año)
- **Exportación de memoria de cálculo** a Word (.docx)
- **Régimen hidráulico seleccionable**: mezcla completa, flujo pistón, flujo disperso

## 📋 Requisitos

- Python 3.9 o superior
- Dependencias:
  ```
  streamlit
  pandas
  numpy
  matplotlib
  python-docx (opcional, para exportar a Word)
  ```

## 🚀 Instalación y uso

1. **Clona el repositorio**:
   ```bash
   git clone https://github.com/<tu-usuario>/ptar-barbosa.git
   cd ptar-barbosa
   ```

2. **Crea un entorno virtual** (recomendado):
   ```bash
   python3 -m venv venv
   source venv/bin/activate    # Linux/macOS
   venv\Scripts\activate       # Windows
   ```

3. **Instala las dependencias**:
   ```bash
   pip install streamlit pandas numpy matplotlib python-docx
   ```

4. **Ejecuta la aplicación**:
   ```bash
   streamlit run app.py
   ```

5. La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`.

## 🧭 Estructura de pestañas

| Pestaña | Contenido |
|---|---|
| 📍 Caudales | Proyección poblacional + caudales Qmd/QMD/QMH |
| 📐 Selección + Costos | Comparación entre las 3 alternativas + recomendación + costos |
| 🏛️ Sedimentador | Diseño RAS Art. 189 + plano esquemático |
| 🌊 Anaerobia | Diseño Mara + plano con talud |
| ⚗️ UASB | Diseño van Haandel + biogás + energía + plano |
| 🌱 Facultativa | Diseño con régimen hidráulico + plano |
| 💧 Maduración | Lagunas en serie con cinética coliformes + plano |
| 🪣 Lodos | Gestión completa de lodos del tren |
| 📈 Sensibilidad | Análisis ante temperatura y DBO |
| 📊 Resumen | Tren completo + cumplimiento Res 0631 + exportación Word |

## 🧮 Modelos y referencias

### Caudales (RAS 2017)
- `Qmd = P × dot × fr / 1000`
- `QMD = k1 × Qmd`
- `QMH = k2 × QMD`

### Laguna Anaerobia (Mara 1997)
- Carga volumétrica: `Lv = f(T)` por temperatura del agua
- `V = L_DBO / Lv`
- Eficiencia DBO: `E = 2T + 20` para T ≤ 25°C

### Laguna Facultativa (Mara 1997)
- `Ls = 350 × (1.107 - 0.002·T)^(T-25)` kg DBO/ha·d
- DBO efluente (mezcla completa): `S = So / (1 + k·TRH)`
- DBO particulada: `1 mg SS/L = 0.3-0.4 mg DBO/L`

### Reactor UASB (van Haandel & Lettinga 1994)
- TRH según T (tabla)
- `Vs = H/TRH` (verificar 0.5-0.7 m/h)
- `Lo = DQO/TRH` (rango ARD 2.5-3.5 kg/m³·d)
- Producción de CH₄: balance de DQO con `Y_acid=0.15`, `Y_metano=0.03`
- `K(T) = P·64/(R·(273+T))` g DQO/L

### Lagunas de Maduración (von Sperling 1999)
- Cinética coliformes: `Kb_T = Kb_20 × 1.19^(T-20)`
- `N = No / (1 + Kb·TRH/n)^n` (mezcla completa en serie)

### Cumplimiento normativo
- **Resolución 0631 de 2015** (PTAR doméstica > 625 hab equiv.):
  - DBO ≤ 90 mg/L
  - DQO ≤ 180 mg/L
  - SST ≤ 90 mg/L
- **Decreto 1076 de 2015** (reúso):
  - Riego restringido: Coliformes ≤ 1.000 NMP/100mL
  - Riego sin restricción: Coliformes ≤ 100 NMP/100mL

## 📚 Referencias bibliográficas

- Mara, D. D. (1997). *Design manual for waste stabilization ponds in India*. Lagoon Technology International.
- Von Sperling, M. y Lemos Chernicharo, C. A. (2005). *Biological wastewater treatment in warm climate regions*. IWA Publishing.
- Van Haandel, A. C. y Lettinga, G. (1994). *Tratamento anaeróbio de esgotos*. Universidade Federal de Campina Grande.
- Qasim, S. R. (1999). *Wastewater Treatment Plants: Planning, Design, and Operation*. CRC Press.
- Colombia. Ministerio de Vivienda. (2017). *RAS - Resolución 0330 de 2017*.
- Colombia. Ministerio de Ambiente. (2015). *Resolución 0631 de 2015 - límites permisibles de vertimientos*.
- Molina Pérez, F. (2020-2024). Apuntes de clase, materia *Sistemas de Tratamiento de Aguas Residuales*, UdeA.

## 📌 Caso de estudio: Barbosa, Antioquia

| Parámetro | Valor |
|---|---|
| Población actual | 55.000 hab |
| Población diseño (25 años, r=1,4%) | ~78.000 hab |
| Dotación neta | 130 L/hab·d |
| Factor de retorno | 0,85 |
| DBO₅ afluente | 280 mg/L |
| DQO afluente | 450 mg/L |
| SST afluente | 220 mg/L |
| Coliformes fecales | 1,5 × 10⁷ NMP/100mL |
| Temperatura aire (mes frío) | 19 °C |
| Área disponible | 60.000 m² |

## 🔬 Validación

Las fórmulas reproducen exactamente:
- El **ejemplo de laguna facultativa** del PDF Clase 09 (DBO efluente 38 mg/L, k corregido 0,41 d⁻¹, eficiencia 81%)
- El **balance de DQO del UASB** del PDF Clase UASB (300 kg/d → 247,35 kg DQO al CH₄, ~95 m³ CH₄/d)

## ⚠️ Limitaciones y trabajo futuro

- Datos hardcodeados de Barbosa (próximo: lectura desde Excel)
- Pretratamiento (rejas, desarenador) no incluido (asumido como aguas arriba del modelo)
- No considera lluvia/evaporación/infiltración
- Costos en US$/hab son referenciales (Clase 09); ajustar a precios COP locales
- No incluye análisis de N y P (solo DBO, DQO, SST, coliformes)

## 👤 Autor

Juan Amud · Ingeniería Sanitaria · Universidad de Antioquia

## 📄 Licencia

Proyecto académico de uso libre con fines educativos.
