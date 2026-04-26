"""
diseno.py — Funciones de ingeniería para el diseño de PTAR.

Módulo independiente de Streamlit, importable por app.py y test_diseno.py.

Referencias:
  - Mara, D. D. (1997).
  - Von Sperling & Lemos Chernicharo (2005).
  - Van Haandel & Lettinga (1994).
  - Qasim (1999).
  - RAS 2017, Resolución 0631 de 2015.
  - Metcalf & Eddy (2014) para lodos activados.
"""

import math


# ============================================================
# CONSTANTES
# ============================================================
DATOS_BARBOSA = {
    "municipio": "Barbosa, Antioquia",
    "anio_actual": 2025,
    "horizonte_diseno": 25,
    "poblacion_actual": 55_000,
    "tasa_crecimiento": 1.4,
    "dotacion_neta": 130,
    "factor_retorno": 0.85,
    "k1": 1.30,
    "k2": 1.45,
    "DBO5": 280.0,
    "DQO": 450.0,
    "SST": 220.0,
    "coliformes_fecales": 1.5e7,
    "T_aire_mes_frio": 19.0,
    "area_disponible": 60_000.0,
}

RES_0631 = {
    "DBO5_max": 90.0,
    "DQO_max": 180.0,
    "SST_max": 90.0,
    "pH_min": 6.0,
    "pH_max": 9.0,
    "grasas_max": 20.0,
    "S_sed_max": 5.0,
}

REUSO_LIMITES = {
    "Riego restringido": 1000,
    "Riego no restringido": 100,
    "Vertimiento a cuerpo receptor": 1e6,
}

COSTOS_RANGOS = {
    "Sedimentador 1°":      {"const": (15, 30), "om": (0.8, 1.5)},
    "Laguna anaerobia":      {"const": (12, 30), "om": (0.8, 1.5)},
    "Reactor UASB":          {"const": (20, 35), "om": (1.5, 3.0)},
    "Laguna facultativa":    {"const": (15, 30), "om": (1.0, 2.0)},
    "Lagunas maduración":    {"const": (8, 15),  "om": (0.5, 1.0)},
    "Lodos activados":       {"const": (40, 80), "om": (3.0, 6.0)},
}

TASAS_LODO = {
    "Sedimentador 1°":     0.06,
    "Laguna anaerobia":    0.05,
    "Reactor UASB":        0.03,
    "Laguna facultativa":  0.04,
    "Laguna maduración":   0.015,
    "Lodos activados":     0.05,
}

# Tabla de O&M por unidad. Cada entry: (parámetro, frecuencia, rango/valor, acción si fuera de rango).
OM_DATA = {
    "Sedimentador 1°": [
        ("pH", "Diaria", "6.5 - 8.5",
            "Investigar si pH < 6 o > 9; afecta sedimentabilidad."),
        ("Tasa de desbordamiento", "Continua", "30-50 m³/m²·d (Qmd)",
            "Verificar caudal; si excede, revisar by-pass."),
        ("TRH", "Continua", "1.5 - 2.5 h",
            "Ajustar caudal si fuera de rango."),
        ("Inspección visual de espumas", "Diaria", "Mínima",
            "Remover con barrenatas; investigar si excesiva."),
        ("Manto de lodos", "Semanal", "< 1/3 H",
            "Programar evacuación cuando supere el límite."),
        ("Concentración SST efluente", "Semanal", "< 100 mg/L",
            "Verificar barrelodos y vertedero."),
        ("DBO efluente", "Mensual", "< 70% del afluente",
            "Revisar TDS y operación general."),
        ("Inspección estructural", "Mensual", "Sin grietas",
            "Reparar fisuras; verificar impermeabilidad."),
    ],
    "Laguna Anaerobia": [
        ("pH", "Semanal", "6.5 - 7.5",
            "Adicionar alcalinidad si pH < 6.5; reducir carga si > 7.5."),
        ("Temperatura del agua", "Semanal", "T diseño ± 3°C",
            "Considerar ajuste de Lv; cubrir en clima frío si aplica."),
        ("Olores (H₂S)", "Diaria", "Mínimos",
            "Verificar carga orgánica y relación DQO/SO₄."),
        ("Profundidad de lodos", "Semestral", "< 1/3 H",
            "Programar evacuación parcial conservando inóculo."),
        ("DBO/DQO efluente", "Mensual", "≤ 50% afluente",
            "Revisar carga volumétrica y posibles cortocircuitos."),
        ("Inspección de talud y borde", "Semestral", "Sin erosión",
            "Reparar erosiones; cortar vegetación."),
        ("Mosquitos", "Semanal", "Mínimos",
            "Mantener nivel uniforme; aplicar control biológico."),
        ("Costra superficial", "Semanal", "< 5 cm",
            "Romper si excede; favorece transferencia gas-líquido."),
    ],
    "Reactor UASB": [
        ("pH efluente", "Diaria", "6.5 - 7.5",
            "Adicionar bicarbonato de sodio si pH baja."),
        ("Alcalinidad total/parcial (AT, AI)", "Semanal", "AI/AT < 0.3",
            "Reducir carga si AI/AT > 0.3 (síntoma de acidificación)."),
        ("AGV efluente", "Semanal", "< 100 mg/L",
            "Indicador temprano de desbalance; reducir carga."),
        ("Temperatura", "Diaria", "T diseño ± 2°C",
            "Verificar estabilidad; baja T frena metanogénesis."),
        ("Caudal y carga orgánica", "Continua", "Lo 2.5-3.5 kg/m³·d",
            "Evitar choques de carga; usar tanque de igualación."),
        ("Producción de biogás", "Diaria", "≈ 0.4 m³/kg DQO removida",
            "Indicador de metanogénesis activa."),
        ("Composición CH₄", "Mensual", "70-80%",
            "% bajo de CH₄ indica problema en metanogénesis."),
        ("Sólidos en efluente (SST)", "Semanal", "< 80 mg/L",
            "Investigar lavado de lodo; reducir Vs."),
        ("Velocidad ascensional", "Continua", "0.5-0.7 m/h (Qmd)",
            "Reducir carga hidráulica si > 1.1 m/h con QMH."),
        ("Perfil de lodos", "Mensual", "Lecho 40-100 g/L; manto 10-30 g/L",
            "Programar purga del lecho cuando ocupe 1/3 de H."),
        ("Edad de lodos (θc)", "Mensual", "> 30 d",
            "Reducir tasa de purga si baja."),
        ("Inspección separador GLS", "Trimestral", "Sin obstrucciones",
            "Limpiar si hay acumulación de espuma."),
    ],
    "Laguna Facultativa": [
        ("pH", "Semanal", "7.0 - 9.0 (día)",
            "pH alto en día indica buena fotosíntesis."),
        ("OD superficial", "Diaria", "> 2 mg/L (día)",
            "Indicador algas saludables; baja indica sobrecarga."),
        ("Temperatura", "Diaria", "T diseño ± 3°C",
            "Afecta cinética k de remoción de DBO."),
        ("Color (algas)", "Visual diaria", "Verde brillante",
            "Investigar si oscuro/anaranjado/rojizo."),
        ("Clorofila a", "Mensual", "200-2000 µg/L",
            "Indicador de biomasa algal."),
        ("DBO total efluente", "Mensual", "< 100 mg/L",
            "Revisar carga superficial Ls."),
        ("SS efluente", "Mensual", "60-100 mg/L (algas)",
            "Considerar pulimiento (filtro de roca o macrófitas)."),
        ("Inspección de talud", "Semestral", "Sin erosión",
            "Reparar y remover vegetación."),
        ("Vegetación riparia", "Mensual", "Mínima en taludes",
            "Cortar para mantener mezcla por viento."),
        ("Profundidad de lodos", "Anual", "< 0.3 m",
            "Programar evacuación cada 5-10 años."),
    ],
    "Lagunas de Maduración": [
        ("Coliformes fecales efluente", "Mensual", "< 1.000 NMP/100mL",
            "Verificar TRH y N° de lagunas; aumentar si no cumple."),
        ("pH", "Mensual", "7.5 - 9.5",
            "pH alto favorece desinfección natural."),
        ("OD", "Mensual", "> 4 mg/L",
            "Indicador de comunidad aerobia depredadora."),
        ("Conductividad", "Mensual", "Estable",
            "Detectar infiltración o evaporación."),
        ("Inspección de bafles (si aplica)", "Trimestral", "Funcionales",
            "Mantener anclaje y tensores."),
        ("Vegetación y macrófitas", "Mensual", "Sin macrófitas no deseadas",
            "Remover; pueden ser refugio de mosquitos."),
        ("Profundidad de lodos", "Anual", "< 0.2 m",
            "Programar evacuación; lodo poco productivo."),
    ],
    "Reactor lodos activados": [
        ("OD en reactor", "Continua", "1.5 - 3.0 mg/L",
            "Ajustar aireación; OD bajo causa malos lodos."),
        ("SSV en reactor (X)", "Diaria", "2.000 - 4.000 mg/L",
            "Ajustar tasa de purga (Qw) según F/M deseado."),
        ("F/M", "Diaria", "0.2 - 0.5 kg DBO/kg SSV·d",
            "Indicador clave de carga; ajustar Qw."),
        ("Edad de lodos (θc)", "Diaria", "5 - 15 d",
            "Aumentar para nitrificar; reducir si bulking."),
        ("IVL (índice volumétrico de lodos)", "Diaria", "80 - 150 mL/g",
            "IVL > 200 indica bulking filamentoso."),
        ("DBO efluente", "Diaria", "< 30 mg/L",
            "Verificar F/M y aireación."),
        ("Turbidez efluente sedimentador", "Diaria", "< 30 NTU",
            "Indicador de pérdida de SSV."),
        ("Energía aireación", "Continua", "0.5 - 1.0 kWh/m³",
            "Optimizar O₂ disuelto."),
        ("Producción de lodo", "Diaria", "Y_obs ≈ 0.4 kg SSV/kg DBO",
            "Disponer en lechos de secado o digestor."),
        ("Coliformes (post-desinfección)", "Diaria", "< 1.000 NMP/100mL",
            "Verificar dosis de cloro/UV."),
    ],
}

# Rangos típicos de diseño para lodos activados (Metcalf & Eddy)
LODOS_ACTIVADOS_DEFAULTS = {
    "TRH_aer_h": 6.0,
    "H_aer": 4.5,
    "F_M": 0.3,                 # kg DBO/kg SSV·d
    "SSV_reactor": 3000,         # mg/L
    "theta_c_d": 10,             # edad de lodos
    "Y_obs": 0.4,                # kg SSV/kg DBO removida
    "TDS_sec": 20,               # m³/m²·d (sed secundario)
    "H_sec": 4.0,
    "ef_dbo": 92,
    "ef_dqo": 85,
    "ef_sst": 92,
    "ef_coli": 90,
    "OR_factor": 1.0,            # kg O₂/kg DBO removida (típico)
    "OE_aireador": 1.5,          # kg O₂/kWh (eficiencia campo)
}


# ============================================================
# FUNCIONES DE INGENIERÍA
# ============================================================
def proyeccion_geometrica(p0, r, n):
    """Proyección poblacional geométrica: P = P0·(1 + r/100)^n."""
    return p0 * (1 + r / 100) ** n


def calcular_caudales(pob, dot, fr, k1, k2):
    """Devuelve (Qmd, QMD, QMH) en m³/d."""
    Qmd = pob * dot * fr / 1000
    QMD = k1 * Qmd
    QMH = k2 * QMD
    return Qmd, QMD, QMH


def temperatura_agua(T_aire):
    """Yáñez (1993): T_agua = 12,7 + 0,54·T_aire."""
    return 12.7 + 0.54 * T_aire


def carga_volumetrica_anaerobia(T):
    """Mara (1997) — Lv kg DBO5/m³·d en función de la temperatura."""
    if T < 10:
        return 0.10
    elif T <= 20:
        return 0.02 * T - 0.10
    elif T <= 25:
        return 0.01 * T + 0.10
    else:
        return 0.35


def eficiencia_anaerobia_dbo(T):
    """Mara (1997) — eficiencia DBO5 [%] en función de la temperatura."""
    if T <= 25:
        return 2 * T + 20
    return 70.0


def carga_superficial_facultativa(T):
    """Mara (1997) — Ls kg DBO5/ha·d."""
    return 350 * (1.107 - 0.002 * T) ** (T - 25)


def k_corregido(k20, T, theta):
    """k_T = k_20·θ^(T-20)."""
    return k20 * (theta ** (T - 20))


def s_mezcla_completa(So, k, TRH, n=1):
    """Modelo de mezcla completa en serie de n lagunas iguales."""
    return So / ((1 + k * TRH / n) ** n)


def s_flujo_piston(So, k, TRH):
    """Modelo de flujo pistón."""
    return So * math.exp(-k * TRH)


def s_flujo_disperso(So, k, TRH, d):
    """Wehner-Wilhelm para flujo disperso en una unidad."""
    a = math.sqrt(1 + 4 * k * TRH * d)
    num = So * 4 * a * math.exp(1 / (2 * d))
    den = (1 + a) ** 2 * math.exp(a / (2 * d)) - (1 - a) ** 2 * math.exp(-a / (2 * d))
    return num / den


def numero_dispersion(L_W):
    """von Sperling (1999): d = 1/(L/W)."""
    return 1 / L_W


def remover(So, k, TRH, regimen, n=1, L_W=2.0):
    """Aplica el régimen hidráulico a n lagunas iguales en serie."""
    if regimen == "Mezcla completa":
        return s_mezcla_completa(So, k, TRH, n)
    if regimen == "Flujo pistón":
        return s_flujo_piston(So, k, TRH * n)
    d = numero_dispersion(L_W)
    s = So
    for _ in range(int(n)):
        s = s_flujo_disperso(s, k, TRH, d)
    return s


def dimensiones_rectangulares(area, L_W):
    """Devuelve (L, W) para una unidad rectangular."""
    if area <= 0 or L_W <= 0:
        return 0.0, 0.0
    W = math.sqrt(area / L_W)
    L = L_W * W
    return L, W


def diametro_circular(area):
    """Diámetro equivalente para área circular."""
    if area <= 0:
        return 0.0
    return math.sqrt(4 * area / math.pi)


def trh_uasb_por_temperatura(T):
    """TRH típico para UASB según T (van Haandel & Lettinga)."""
    if T < 16:
        return 14.0
    elif T < 20:
        return 12.0
    elif T <= 26:
        return 8.0
    else:
        return 6.0


def K_metano(T, P=1.0, R=0.08206):
    """K(T) = P·64/(R·(273+T)) en g DQO/L de CH4 (= kg/m³)."""
    return P * 64 / (R * (273 + T))


# ============================================================
# LODOS, COSTOS, ENERGÍA, CUMPLIMIENTO
# ============================================================
def calcular_lodos(unidad_nombre, pob, A_unidad, H_util,
                    densidad=1100, pct_sst=0.05, carga_lecho=150):
    """Manejo de lodos por unidad."""
    tasa = TASAS_LODO.get(unidad_nombre, 0.05)
    V_anual = pob * tasa
    altura_anual = V_anual / A_unidad if A_unidad > 0 else 0
    altura_max = H_util / 3
    anos_evac = (altura_max / altura_anual) if altura_anual > 0 else float("inf")
    masa_sst = V_anual * densidad * pct_sst
    A_lecho = masa_sst / carga_lecho if carga_lecho > 0 else 0
    return {
        "tasa": tasa,
        "V_anual": V_anual,
        "altura_anual_cm": altura_anual * 100,
        "anos_evacuacion": anos_evac,
        "masa_sst_anual": masa_sst,
        "A_lecho": A_lecho,
    }


def estimar_costos(opcion, pob, anios=25):
    """Estima costos según rangos US$/hab."""
    if opcion not in COSTOS_RANGOS:
        return None
    r = COSTOS_RANGOS[opcion]
    c_med = (r["const"][0] + r["const"][1]) / 2
    om_med = (r["om"][0] + r["om"][1]) / 2
    return {
        "construccion_min": r["const"][0] * pob,
        "construccion_max": r["const"][1] * pob,
        "construccion_med": c_med * pob,
        "om_anual_min": r["om"][0] * pob,
        "om_anual_max": r["om"][1] * pob,
        "om_anual_med": om_med * pob,
        "total_25_med": c_med * pob + om_med * pob * anios,
    }


def energia_biogas(Q_CH4_d, eficiencia=0.35, PCI=9.97):
    """Energía recuperable del biogás."""
    e_term = Q_CH4_d * PCI
    e_elec = e_term * eficiencia
    return {
        "PCI": PCI,
        "energia_termica_d": e_term,
        "energia_electrica_d": e_elec,
        "MWh_anio": e_elec * 365 / 1000,
        "potencia_kw": e_elec / 24,
    }


def verificar_res0631(DBO, DQO, SST, Coli):
    """Verifica cumplimiento contra Res 0631 y Decreto 1076."""
    items = [
        ("DBO₅ ≤ 90 mg/L (Res 0631)", DBO, RES_0631["DBO5_max"], "mg/L"),
        ("DQO ≤ 180 mg/L (Res 0631)", DQO, RES_0631["DQO_max"], "mg/L"),
        ("SST ≤ 90 mg/L (Res 0631)", SST, RES_0631["SST_max"], "mg/L"),
        ("Coliformes ≤ 1.000 (riego restringido, Dec. 1076)",
            Coli, REUSO_LIMITES["Riego restringido"], "NMP/100mL"),
        ("Coliformes ≤ 100 (riego sin restricción, Dec. 1076)",
            Coli, REUSO_LIMITES["Riego no restringido"], "NMP/100mL"),
    ]
    rows = []
    for nombre, valor, limite, unidad in items:
        rows.append({
            "Parámetro": nombre,
            "Valor": valor,
            "Límite": limite,
            "Unidad": unidad,
            "Cumple": "✓" if valor <= limite else "✗",
        })
    return rows


# ============================================================
# DISEÑO DE UNIDADES
# ============================================================
def disenar_sedimentador_primario(Qmd, QMH, DBO, DQO, SST, Coli,
                                    TDS_med=40, TDS_pico=100,
                                    H=3.0, LW=2.0, n_paralelo=1,
                                    ef_dbo=35, ef_dqo=35, ef_sst=60, ef_coli=30):
    """Sedimentador primario (RAS Art. 189 / Qasim)."""
    A_med = Qmd / TDS_med
    A_pico = QMH / TDS_pico
    A = max(A_med, A_pico)
    A_unit = A / n_paralelo
    V = A * H
    V_unit = V / n_paralelo
    TRH_h = V * 24 / Qmd
    L_unit, W_unit = dimensiones_rectangulares(A_unit, LW)
    return {
        "tipo": "Sedimentador 1°",
        "A": A, "A_unit": A_unit, "A_med": A_med, "A_pico": A_pico,
        "V": V, "V_unit": V_unit, "H": H, "L": L_unit, "W": W_unit,
        "n_paralelo": n_paralelo,
        "TRH_h": TRH_h, "TDS_med": TDS_med, "TDS_pico": TDS_pico,
        "DBO_out": DBO * (1 - ef_dbo / 100),
        "DQO_out": DQO * (1 - ef_dqo / 100),
        "SST_out": SST * (1 - ef_sst / 100),
        "Coli_out": Coli * (1 - ef_coli / 100),
        "ef_dbo": ef_dbo, "ef_dqo": ef_dqo,
        "ef_sst": ef_sst, "ef_coli": ef_coli,
    }


def disenar_laguna_anaerobia(Q, DBO, DQO, SST, Coli, T,
                                Lv=None, H=4.0, LW=2.0, n_paralelo=1,
                                talud=2.0,
                                ef_dqo=65, ef_sst=70, ef_coli=90):
    """Laguna anaerobia (Mara 1997)."""
    if Lv is None:
        Lv = carga_volumetrica_anaerobia(T)
    L_org = Q * DBO / 1000
    V = L_org / Lv
    V_unit = V / n_paralelo
    A = V / H
    A_unit = A / n_paralelo
    L_d, W = dimensiones_rectangulares(A_unit, LW)
    TRH_d = V / Q
    ef_dbo = eficiencia_anaerobia_dbo(T)
    return {
        "tipo": "Laguna anaerobia",
        "Lv": Lv, "L_org": L_org,
        "A": A, "A_unit": A_unit, "V": V, "V_unit": V_unit,
        "H": H, "L": L_d, "W": W, "talud": talud, "n_paralelo": n_paralelo,
        "TRH_d": TRH_d, "TRH_h": TRH_d * 24,
        "DBO_out": DBO * (1 - ef_dbo / 100),
        "DQO_out": DQO * (1 - ef_dqo / 100),
        "SST_out": SST * (1 - ef_sst / 100),
        "Coli_out": Coli * (1 - ef_coli / 100),
        "ef_dbo": ef_dbo, "ef_dqo": ef_dqo,
        "ef_sst": ef_sst, "ef_coli": ef_coli,
    }


def disenar_reactor_uasb(Q, QMH, DBO, DQO, SST, Coli, T,
                           TRH_h=None, H=5.0, LW=1.0,
                           forma="Circular", n_paralelo=1,
                           Y_acid=0.15, Y_metano=0.03,
                           ef_dbo=70, ef_dqo=70, ef_sst=70, ef_coli=90):
    """Reactor UASB (van Haandel & Lettinga)."""
    if TRH_h is None:
        TRH_h = trh_uasb_por_temperatura(T)
    TRH_d = TRH_h / 24
    V = Q * TRH_d
    V_unit = V / n_paralelo
    A = V / H
    A_unit = A / n_paralelo
    L_d, W = dimensiones_rectangulares(A_unit, LW)
    D = diametro_circular(A_unit)
    Vs_md = H / TRH_d
    Vs_mh = Vs_md / 24
    Vs_mh_QMH = (QMH * H / V) / 24
    Lh = 1 / TRH_d
    Lo = (DQO / 1000) / TRH_d

    DBO_out = DBO * (1 - ef_dbo / 100)
    DQO_out = DQO * (1 - ef_dqo / 100)
    SST_out = SST * (1 - ef_sst / 100)
    Coli_out = Coli * (1 - ef_coli / 100)

    DQO_rem = (DQO - DQO_out) * Q / 1000
    DQO_disp = DQO_rem * (1 - Y_acid)
    DQO_metano = DQO_disp * (1 - Y_metano)
    K_T = K_metano(T)
    Q_CH4 = DQO_metano / K_T if K_T > 0 else 0.0

    return {
        "tipo": "Reactor UASB",
        "TRH_h": TRH_h, "TRH_d": TRH_d,
        "V": V, "V_unit": V_unit, "A": A, "A_unit": A_unit,
        "H": H, "L": L_d, "W": W, "D": D, "forma": forma,
        "n_paralelo": n_paralelo,
        "Vs_mh": Vs_mh, "Vs_mh_QMH": Vs_mh_QMH,
        "Lh": Lh, "Lo": Lo,
        "DBO_out": DBO_out, "DQO_out": DQO_out,
        "SST_out": SST_out, "Coli_out": Coli_out,
        "ef_dbo": ef_dbo, "ef_dqo": ef_dqo,
        "ef_sst": ef_sst, "ef_coli": ef_coli,
        "DQO_rem": DQO_rem, "DQO_metano": DQO_metano,
        "Q_CH4": Q_CH4, "K_T": K_T,
        "Y_acid": Y_acid, "Y_metano": Y_metano,
    }


def disenar_lodos_activados(Q, DBO, DQO, SST, Coli,
                              TRH_h=None, H_aer=None, F_M=None,
                              SSV=None, theta_c=None, Y_obs=None,
                              TDS_sec=None, H_sec=None,
                              ef_dbo=None, ef_dqo=None, ef_sst=None, ef_coli=None,
                              OR_factor=None, OE_aireador=None):
    """
    Diseño simplificado de lodos activados convencionales con sedimentador
    secundario y desinfección. Metcalf & Eddy (2014).

    Q en m³/d, DBO/DQO/SST en mg/L, Coli en NMP/100mL.
    """
    d = LODOS_ACTIVADOS_DEFAULTS
    TRH_h = TRH_h if TRH_h is not None else d["TRH_aer_h"]
    H_aer = H_aer if H_aer is not None else d["H_aer"]
    F_M = F_M if F_M is not None else d["F_M"]
    SSV = SSV if SSV is not None else d["SSV_reactor"]
    theta_c = theta_c if theta_c is not None else d["theta_c_d"]
    Y_obs = Y_obs if Y_obs is not None else d["Y_obs"]
    TDS_sec = TDS_sec if TDS_sec is not None else d["TDS_sec"]
    H_sec = H_sec if H_sec is not None else d["H_sec"]
    ef_dbo = ef_dbo if ef_dbo is not None else d["ef_dbo"]
    ef_dqo = ef_dqo if ef_dqo is not None else d["ef_dqo"]
    ef_sst = ef_sst if ef_sst is not None else d["ef_sst"]
    ef_coli = ef_coli if ef_coli is not None else d["ef_coli"]
    OR_factor = OR_factor if OR_factor is not None else d["OR_factor"]
    OE_aireador = OE_aireador if OE_aireador is not None else d["OE_aireador"]

    # 1. Reactor de aireación (CSTR)
    TRH_d = TRH_h / 24
    V_aer = Q * TRH_d
    A_aer = V_aer / H_aer
    L_aer, W_aer = dimensiones_rectangulares(A_aer, 1.5)

    # 2. Verificación F/M
    L_DBO = Q * DBO / 1000              # kg DBO/d afluente al reactor
    masa_SSV = V_aer * SSV / 1000       # kg SSV en reactor
    F_M_calc = L_DBO / masa_SSV if masa_SSV > 0 else 0

    # 3. Sedimentador secundario
    A_sec = Q / TDS_sec
    V_sec = A_sec * H_sec
    L_sec, W_sec = dimensiones_rectangulares(A_sec, 2.0)

    # 4. Salidas
    DBO_out = DBO * (1 - ef_dbo / 100)
    DQO_out = DQO * (1 - ef_dqo / 100)
    SST_out = SST * (1 - ef_sst / 100)
    Coli_out = Coli * (1 - ef_coli / 100)

    # 5. Producción de lodo
    DBO_rem = Q * (DBO - DBO_out) / 1000     # kg DBO/d removida
    lodo_kg_d = Y_obs * DBO_rem               # kg SSV/d producidos
    Qw = lodo_kg_d / SSV * 1000               # m³/d a purgar (asumiendo SSV en lodo de purga)

    # 6. Requerimiento de oxígeno
    OR_kg_d = OR_factor * DBO_rem             # kg O₂/d
    energia_kwh_d = OR_kg_d / OE_aireador     # kWh/d

    # 7. Área total
    A_total = A_aer + A_sec

    return {
        "tipo": "Lodos activados",
        "TRH_h": TRH_h, "V_aer": V_aer, "A_aer": A_aer, "H_aer": H_aer,
        "L_aer": L_aer, "W_aer": W_aer,
        "F_M": F_M_calc, "SSV": SSV, "theta_c": theta_c,
        "A_sec": A_sec, "V_sec": V_sec, "H_sec": H_sec,
        "L_sec": L_sec, "W_sec": W_sec,
        "A_total": A_total,
        "DBO_out": DBO_out, "DQO_out": DQO_out,
        "SST_out": SST_out, "Coli_out": Coli_out,
        "ef_dbo": ef_dbo, "ef_dqo": ef_dqo,
        "ef_sst": ef_sst, "ef_coli": ef_coli,
        "DBO_rem": DBO_rem,
        "lodo_kg_d": lodo_kg_d, "Qw": Qw,
        "OR_kg_d": OR_kg_d, "energia_kwh_d": energia_kwh_d,
        "potencia_kw": energia_kwh_d / 24,
    }


def recomendar_primario(area_disp, sed, ana, uasb):
    """Recomienda el tratamiento primario según área disponible."""
    viable_sed = sed["A"] <= area_disp
    viable_ana = ana["A"] <= area_disp
    viable_uasb = uasb["A"] <= area_disp
    viables = []
    if viable_sed: viables.append("Sedimentador 1°")
    if viable_ana: viables.append("Laguna anaerobia")
    if viable_uasb: viables.append("Reactor UASB")

    if not viables:
        return ("Ninguna opción cabe", "danger",
                "Área insuficiente. Considera aumentar el área "
                "o usar reactores UASB modulares.", viables)

    if viable_uasb:
        rec = "Reactor UASB"
        just = ("UASB es la opción más recomendable: alta eficiencia (65-75%), "
                "huella compacta, recuperación de biogás. Considera arranque ~6 meses.")
    elif viable_ana:
        rec = "Laguna anaerobia"
        just = ("Laguna anaerobia viable, eficiencia DBO según T. Robusta, "
                "pero requiere más área y puede generar olores.")
    else:
        rec = "Sedimentador 1°"
        just = ("Solo el sedimentador cabe. Eficiencia DBO baja (30-40%); "
                "requiere secundario robusto.")
    return rec, "success", just, viables
