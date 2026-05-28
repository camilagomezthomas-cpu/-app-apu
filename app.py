import streamlit as st
import pandas as pd
from io import StringIO

st.set_page_config(
    page_title="APU Presupuestos",
    page_icon="📊",
    layout="wide"
)

# =====================================================
# DATOS GENERALES
# =====================================================

JORNADA_HORAS = 8
PRESTACIONES_SOCIALES = 1.65

# =====================================================
# BASES DE DATOS
# =====================================================

MANO_OBRA_DB = {
    "Oficial": 100000,
    "Ayudante": 71428.57,
    "Obrero": 70000,
    "Maestro de obra": 140000,
    "Operador equipo": 120000,
    "Soldador": 130000,
    "Armador": 110000,
}

EQUIPOS_DB = {
    "Retroexcavadora": {"tipo": "75 HP", "unidad": "h", "tarifa_hora": 90000, "rendimiento": 8.0},
    "Volqueta": {"tipo": "6.5 m³", "unidad": "h", "tarifa_hora": 75000, "rendimiento": 6.5},
    "Vibrador de concreto": {"tipo": "Eléctrico", "unidad": "h", "tarifa_hora": 35000, "rendimiento": 3.0},
    "Mezcladora": {"tipo": "Concreto", "unidad": "h", "tarifa_hora": 60000, "rendimiento": 2.5},
    "Formaleta / herramienta menor": {"tipo": "Manual", "unidad": "h", "tarifa_hora": 25000, "rendimiento": 10.0},
    "Soldadora": {"tipo": "Eléctrica", "unidad": "h", "tarifa_hora": 85000, "rendimiento": 80.0},
}

APUS = {
    "Excavación mecánica": {
        "unidad": "m³",
        "capitulo": "MOVIMIENTO DE TIERRAS",
        "equipo_default": ["Retroexcavadora", "Volqueta"],
        "mano_default": ["Operador equipo", "Ayudante"],
        "rendimiento": 8.0,
        "materiales": {},
        "checklist": [
            "Replanteo del área de excavación verificado",
            "Profundidad y ancho de excavación revisados",
            "Taludes o entibado revisados según condición del terreno",
            "Material excavado retirado adecuadamente",
            "Botadero autorizado definido",
            "Uso de EPP verificado en campo",
        ],
    },
    "Zapata en concreto": {
        "unidad": "m³",
        "capitulo": "CIMENTACIÓN",
        "equipo_default": ["Mezcladora", "Vibrador de concreto"],
        "mano_default": ["Oficial", "Ayudante"],
        "rendimiento": 2.5,
        "materiales": {
            "Concreto": {"unidad": "m³", "cantidad": 1.05, "precio": 420000},
            "Acero de refuerzo": {"unidad": "kg", "cantidad": 85, "precio": 5200},
            "Alambre negro": {"unidad": "kg", "cantidad": 1.5, "precio": 8000},
        },
        "checklist": [
            "Excavación de zapata conforme a planos",
            "Solado o limpieza de fondo verificado",
            "Acero colocado según diseño",
            "Formaleta revisada y asegurada",
            "Concreto vibrado correctamente",
            "Curado inicial realizado",
        ],
    },
    "Viga en concreto": {
        "unidad": "m³",
        "capitulo": "ESTRUCTURA EN CONCRETO",
        "equipo_default": ["Vibrador de concreto", "Formaleta / herramienta menor"],
        "mano_default": ["Oficial", "Ayudante"],
        "rendimiento": 2.0,
        "materiales": {
            "Concreto": {"unidad": "m³", "cantidad": 1.05, "precio": 420000},
            "Acero de refuerzo": {"unidad": "kg", "cantidad": 95, "precio": 5200},
            "Formaleta": {"unidad": "m²", "cantidad": 6, "precio": 35000},
        },
        "checklist": [
            "Acero de refuerzo instalado según planos",
            "Formaleta alineada y nivelada",
            "Separadores colocados",
            "Concreto vaciado correctamente",
            "Vibrado realizado",
            "Curado verificado",
        ],
    },
    "Losa aligerada": {
        "unidad": "m²",
        "capitulo": "ESTRUCTURA EN CONCRETO",
        "equipo_default": ["Vibrador de concreto", "Formaleta / herramienta menor"],
        "mano_default": ["Oficial", "Ayudante"],
        "rendimiento": 12.0,
        "materiales": {
            "Concreto": {"unidad": "m³", "cantidad": 0.12, "precio": 420000},
            "Acero de refuerzo": {"unidad": "kg", "cantidad": 12, "precio": 5200},
            "Aligerante / casetón": {"unidad": "und", "cantidad": 1, "precio": 18000},
        },
        "checklist": [
            "Formaleta instalada y apuntalada",
            "Aligerantes o casetones colocados",
            "Acero de refuerzo revisado",
            "Instalaciones embebidas verificadas",
            "Concreto vaciado y vibrado",
            "Curado realizado",
        ],
    },
    "Estructura metálica": {
        "unidad": "kg",
        "capitulo": "ESTRUCTURA METÁLICA",
        "equipo_default": ["Soldadora"],
        "mano_default": ["Soldador", "Ayudante"],
        "rendimiento": 80.0,
        "materiales": {
            "Acero estructural": {"unidad": "kg", "cantidad": 1.0, "precio": 7800},
            "Electrodos / soldadura": {"unidad": "kg", "cantidad": 0.03, "precio": 18000},
            "Pintura anticorrosiva": {"unidad": "gl", "cantidad": 0.01, "precio": 95000},
        },
        "checklist": [
            "Material metálico certificado",
            "Cortes y perforaciones revisados",
            "Soldadura inspeccionada visualmente",
            "Alineación y nivelación verificadas",
            "Pintura anticorrosiva aplicada",
            "Montaje seguro en campo",
        ],
    },
}

# =====================================================
# FUNCIONES
# =====================================================

def pesos(valor):
    return f"$ {float(valor):,.2f}"

def formato(valor, decimales=2):
    try:
        return f"{float(valor):,.{decimales}f}"
    except:
        return valor

def descargar_csv(df):
    return df.to_csv(index=False).encode("utf-8-sig")

# =====================================================
# INTERFAZ
# =====================================================

st.title("📊 MATRIZ APU - SISTEMA DE PRESUPUESTOS DE OBRA CIVIL")
st.caption("Trabajo académico universitario - Análisis de Precios Unitarios")

st.sidebar.header("Menú de APU")
apu = st.sidebar.selectbox("Seleccione el ítem", list(APUS.keys()))
data_apu = APUS[apu]

# =====================================================
# DATOS DEL PROYECTO
# =====================================================

st.subheader("DATOS DEL PROYECTO")

col1, col2 = st.columns(2)

with col1:
    proyecto = st.text_input("Proyecto", "UNIVERSIDAD MILITAR NUEVA GRANADA - PRESUPUESTO DE OBRA CIVIL")
    contrato = st.text_input("Integrantes", "CAMILA GÓMEZ - CHAROL RAMÍREZ")
    anio = st.number_input("Año", value=2026, step=1)

with col2:
    capitulo = st.text_input("Capítulo", data_apu["capitulo"])
    item = st.text_input("Ítem", apu)
    unidad = st.text_input("Unidad del APU", data_apu["unidad"])

st.divider()

# =====================================================
# PARÁMETROS SEGÚN APU
# =====================================================

st.subheader("1. PARÁMETROS DE CÁLCULO")

col3, col4, col5 = st.columns(3)

with col3:
    cantidad_obra = st.number_input(f"Cantidad de obra ({unidad})", value=100.0, min_value=0.0)

with col4:
    rendimiento_base = st.number_input(
        f"Rendimiento de la actividad ({unidad}/h)",
        value=float(data_apu["rendimiento"]),
        min_value=0.01
    )

with col5:
    aiu_porcentaje = st.number_input("AIU (%)", value=25.0, min_value=0.0)

if apu == "Excavación mecánica":
    st.markdown("### Parámetros geométricos de excavación")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        base_menor = st.number_input("Base menor B1 (m)", value=1.8, min_value=0.0)

    with c2:
        base_mayor = st.number_input("Base mayor B2 (m)", value=2.8, min_value=0.0)

    with c3:
        longitud_tramo = st.number_input("Longitud L (m)", value=50.0, min_value=0.0)

    with c4:
        profundidad = st.number_input("Profundidad H (m)", value=1.5, min_value=0.0)

    factor_expansion = st.number_input("Factor de expansión del material", value=1.25, min_value=1.0)

    area_perfil = ((base_menor + base_mayor) / 2) * profundidad
    volumen_excavacion = area_perfil * longitud_tramo
    volumen_expansion = volumen_excavacion * factor_expansion
    cantidad_obra = volumen_excavacion

    parametros_df = pd.DataFrame({
        "PARÁMETRO": [
            "Área del perfil trapezoidal",
            "Volumen de excavación en banco",
            "Factor de expansión",
            "Volumen expandido para transporte",
            "Rendimiento de excavación"
        ],
        "VALOR": [
            area_perfil,
            volumen_excavacion,
            factor_expansion,
            volumen_expansion,
            rendimiento_base
        ],
        "UNIDAD": [
            "m²",
            "m³",
            "-",
            "m³",
            "m³/h"
        ]
    })

else:
    volumen_expansion = 0
    parametros_df = pd.DataFrame({
        "PARÁMETRO": [
            "Cantidad de obra",
            "Rendimiento de actividad",
            "Jornada laboral",
            "AIU"
        ],
        "VALOR": [
            cantidad_obra,
            rendimiento_base,
            JORNADA_HORAS,
            aiu_porcentaje
        ],
        "UNIDAD": [
            unidad,
            f"{unidad}/h",
            "h/día",
            "%"
        ]
    })

st.dataframe(parametros_df, use_container_width=True)

st.divider()

# =====================================================
# EQUIPO
# =====================================================

st.subheader("2. EQUIPO")

equipos_seleccionados = st.multiselect(
    "Seleccione equipos",
    list(EQUIPOS_DB.keys()),
    default=data_apu["equipo_default"]
)

filas_equipo = []

for equipo in equipos_seleccionados:
    datos = EQUIPOS_DB[equipo]

    st.markdown(f"#### {equipo}")

    e1, e2, e3 = st.columns(3)

    with e1:
        cantidad_equipo = st.number_input(
            f"Cantidad de {equipo}",
            value=1.0,
            min_value=0.0,
            key=f"cantidad_equipo_{equipo}"
        )

    with e2:
        tarifa_hora = st.number_input(
            f"Tarifa {equipo} ($/h)",
            value=float(datos["tarifa_hora"]),
            min_value=0.0,
            key=f"tarifa_{equipo}"
        )

    with e3:
        rendimiento_equipo = st.number_input(
            f"Rendimiento {equipo} ({unidad}/h)",
            value=float(datos["rendimiento"]),
            min_value=0.01,
            key=f"rend_{equipo}"
        )

    costo_unitario_equipo = (cantidad_equipo * tarifa_hora) / rendimiento_equipo

    filas_equipo.append({
        "DESCRIPCIÓN": equipo.upper(),
        "TIPO": datos["tipo"],
        "UND": "h",
        "CANTIDAD": cantidad_equipo,
        "TARIFA": tarifa_hora,
        f"RENDIMIENTO ({unidad}/h)": rendimiento_equipo,
        "VALOR UNITARIO": costo_unitario_equipo,
        "VALOR PARCIAL": costo_unitario_equipo * cantidad_obra
    })

equipo_df = pd.DataFrame(filas_equipo)
subtotal_equipo_unitario = equipo_df["VALOR UNITARIO"].sum() if not equipo_df.empty else 0
subtotal_equipo_total = subtotal_equipo_unitario * cantidad_obra

st.dataframe(equipo_df, use_container_width=True)
st.success(f"Sub-Total Equipo Unitario: {pesos(subtotal_equipo_unitario)} / {unidad}")

st.divider()

# =====================================================
# MATERIALES
# =====================================================

st.subheader("3. MATERIALES DE OBRA")

filas_materiales = []

if data_apu["materiales"]:
    for material, datos in data_apu["materiales"].items():
        m1, m2 = st.columns(2)

        with m1:
            cantidad_mat = st.number_input(
                f"Cantidad {material} por {unidad}",
                value=float(datos["cantidad"]),
                min_value=0.0,
                key=f"cant_{material}"
            )

        with m2:
            precio_mat = st.number_input(
                f"Precio unitario {material}",
                value=float(datos["precio"]),
                min_value=0.0,
                key=f"precio_{material}"
            )

        valor_unitario = cantidad_mat * precio_mat

        filas_materiales.append({
            "DESCRIPCIÓN": material.upper(),
            "UNIDAD": datos["unidad"],
            f"CANTIDAD POR {unidad}": cantidad_mat,
            "PRECIO UNITARIO": precio_mat,
            "VALOR UNITARIO": valor_unitario,
            "VALOR PARCIAL": valor_unitario * cantidad_obra
        })
else:
    st.info("Para excavación mecánica no se consideran materiales permanentes; el combustible o insumos pueden incluirse dentro de la tarifa del equipo.")

materiales_df = pd.DataFrame(filas_materiales)
subtotal_materiales_unitario = materiales_df["VALOR UNITARIO"].sum() if not materiales_df.empty else 0
subtotal_materiales_total = subtotal_materiales_unitario * cantidad_obra

st.dataframe(materiales_df, use_container_width=True)
st.success(f"Sub-Total Materiales Unitario: {pesos(subtotal_materiales_unitario)} / {unidad}")

st.divider()

# =====================================================
# TRANSPORTE
# =====================================================

st.subheader("4. TRANSPORTE")

transporte_df = pd.DataFrame()
subtotal_transporte_unitario = 0
subtotal_transporte_total = 0

if apu == "Excavación mecánica":
    t1, t2, t3 = st.columns(3)

    with t1:
        distancia_botadero = st.number_input("Distancia al botadero (km)", value=15.0, min_value=0.0)

    with t2:
        tarifa_transporte = st.number_input("Tarifa transporte ($/m³-km)", value=1500.0, min_value=0.0)

    with t3:
        tarifa_vertimiento = st.number_input("Tarifa vertimiento / botadero ($/m³)", value=80000.0, min_value=0.0)

    cantidad_transportada = volumen_expansion
    m3_km = cantidad_transportada * distancia_botadero
    valor_transporte_material = m3_km * tarifa_transporte
    valor_vertimiento = cantidad_transportada * tarifa_vertimiento
    subtotal_transporte_total = valor_transporte_material + valor_vertimiento
    subtotal_transporte_unitario = subtotal_transporte_total / cantidad_obra if cantidad_obra > 0 else 0

    transporte_df = pd.DataFrame({
        "ÍTEM": ["MATERIAL EXCAVADO", "BOTADERO"],
        "DISTANCIA (km)": [distancia_botadero, ""],
        "CANTIDAD (m³)": [cantidad_transportada, cantidad_transportada],
        "m³-km": [m3_km, ""],
        "TARIFA": [tarifa_transporte, tarifa_vertimiento],
        "VALOR PARCIAL": [valor_transporte_material, valor_vertimiento]
    })

    st.dataframe(transporte_df, use_container_width=True)
    st.success(f"Sub-Total Transporte Unitario: {pesos(subtotal_transporte_unitario)} / m³")

else:
    st.info("Para este APU el transporte no aplica directamente o se considera incluido en materiales/equipo.")

st.divider()

# =====================================================
# MANO DE OBRA
# =====================================================

st.subheader("5. MANO DE OBRA")

trabajadores_seleccionados = st.multiselect(
    "Seleccione trabajadores",
    list(MANO_OBRA_DB.keys()),
    default=data_apu["mano_default"]
)

filas_mano = []

for trabajador in trabajadores_seleccionados:
    mo1, mo2 = st.columns(2)

    with mo1:
        cantidad_trabajadores = st.number_input(
            f"Cantidad de {trabajador}",
            min_value=0.0,
            value=1.0,
            step=1.0,
            key=f"cant_trab_{trabajador}"
        )

    with mo2:
        jornal = st.number_input(
            f"Jornal diario {trabajador}",
            min_value=0.0,
            value=float(MANO_OBRA_DB[trabajador]),
            step=1000.0,
            key=f"jornal_{trabajador}"
        )

    jornal_total = jornal * PRESTACIONES_SOCIALES
    costo_hora = jornal_total / JORNADA_HORAS
    valor_unitario_mano = (cantidad_trabajadores * costo_hora) / rendimiento_base

    filas_mano.append({
        "TRABAJADOR": trabajador.upper(),
        "CANTIDAD": cantidad_trabajadores,
        "JORNAL": jornal,
        "PRESTACIONES": PRESTACIONES_SOCIALES,
        "JORNAL TOTAL": jornal_total,
        "COSTO HORA": costo_hora,
        f"RENDIMIENTO ({unidad}/h)": rendimiento_base,
        "VALOR UNITARIO": valor_unitario_mano,
        "VALOR PARCIAL": valor_unitario_mano * cantidad_obra
    })

mano_df = pd.DataFrame(filas_mano)
subtotal_mano_unitario = mano_df["VALOR UNITARIO"].sum() if not mano_df.empty else 0
subtotal_mano_total = subtotal_mano_unitario * cantidad_obra

st.dataframe(mano_df, use_container_width=True)
st.success(f"Sub-Total Mano de Obra Unitario: {pesos(subtotal_mano_unitario)} / {unidad}")

st.divider()

# =====================================================
# LISTA DE CHEQUEO
# =====================================================

st.subheader("6. LISTA DE CHEQUEO EN CAMPO")

checks = []
for punto in data_apu["checklist"]:
    checks.append(st.checkbox(punto))

cumplimiento = (sum(checks) / len(checks)) * 100 if checks else 0
st.progress(cumplimiento / 100)
st.info(f"Cumplimiento de lista de chequeo: {cumplimiento:.1f}%")

st.divider()

# =====================================================
# RESUMEN
# =====================================================

costo_directo_unitario = (
    subtotal_equipo_unitario +
    subtotal_materiales_unitario +
    subtotal_transporte_unitario +
    subtotal_mano_unitario
)

aiu_unitario = costo_directo_unitario * (aiu_porcentaje / 100)
valor_unitario_total = costo_directo_unitario + aiu_unitario
valor_total_apu = valor_unitario_total * cantidad_obra

r1, r2, r3, r4 = st.columns(4)

r1.metric("Costo directo unitario", pesos(costo_directo_unitario))
r2.metric("AIU unitario", pesos(aiu_unitario))
r3.metric("Valor unitario total", pesos(valor_unitario_total))
r4.metric("Valor total del ítem", pesos(valor_total_apu))

st.divider()

# =====================================================
# TABLA FINAL TIPO EXCEL
# =====================================================

st.subheader("7. TABLA COMPLETA DEL APU")

html = f"""
<style>
.apu-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
    font-family: Arial, sans-serif;
    background-color: white;
    color: black;
}}
.apu-table th, .apu-table td {{
    border: 1px solid black;
    padding: 5px;
    text-align: center;
    color: black;
}}
.section {{
    background-color: #e6e6e6;
    font-weight: bold;
    text-align: left !important;
}}
.subtotal {{
    font-weight: bold;
    text-align: right !important;
}}
.total {{
    font-weight: bold;
    background-color: #d9d9d9;
}}
</style>

<table class="apu-table">
<tr><td colspan="8"><b>ANÁLISIS DE PRECIOS UNITARIOS APU</b></td></tr>
<tr><td>PROYECTO</td><td colspan="7">{proyecto}</td></tr>
<tr><td>INTEGRANTES</td><td colspan="7">{contrato}</td></tr>
<tr><td>AÑO</td><td colspan="7">{anio}</td></tr>
<tr><td>CAPÍTULO</td><td colspan="7">{capitulo}</td></tr>
<tr><td>ÍTEM</td><td colspan="7">{item}</td></tr>
<tr><td>UNIDAD</td><td colspan="7">{unidad}</td></tr>
<tr><td>CANTIDAD DE OBRA</td><td colspan="7">{formato(cantidad_obra, 3)} {unidad}</td></tr>

<tr><td colspan="8" class="section">PARÁMETROS DE CÁLCULO</td></tr>
<tr><th>PARÁMETRO</th><th colspan="3">VALOR</th><th colspan="4">UNIDAD</th></tr>
"""

for _, row in parametros_df.iterrows():
    html += f"""
    <tr>
    <td>{row['PARÁMETRO']}</td>
    <td colspan="3">{formato(row['VALOR'], 3)}</td>
    <td colspan="4">{row['UNIDAD']}</td>
    </tr>
    """

html += """
<tr><td colspan="8" class="section">1. EQUIPO</td></tr>
<tr>
<th>DESCRIPCIÓN</th><th>TIPO</th><th>UND</th><th>CANTIDAD</th>
<th>TARIFA</th><th>RENDIMIENTO</th><th>VALOR UNITARIO</th><th>VALOR PARCIAL</th>
</tr>
"""

for _, row in equipo_df.iterrows():
    html += f"""
    <tr>
    <td>{row['DESCRIPCIÓN']}</td>
    <td>{row['TIPO']}</td>
    <td>{row['UND']}</td>
    <td>{formato(row['CANTIDAD'], 2)}</td>
    <td>{pesos(row['TARIFA'])}</td>
    <td>{formato(row[f'RENDIMIENTO ({unidad}/h)'], 2)}</td>
    <td>{pesos(row['VALOR UNITARIO'])}</td>
    <td>{pesos(row['VALOR PARCIAL'])}</td>
    </tr>
    """

html += f"""
<tr><td colspan="7" class="subtotal">Sub-Total Equipo Unitario</td><td>{pesos(subtotal_equipo_unitario)}</td></tr>

<tr><td colspan="8" class="section">2. MATERIALES DE OBRA</td></tr>
<tr>
<th>DESCRIPCIÓN</th><th colspan="2">UNIDAD</th><th colspan="2">CANTIDAD</th>
<th>PRECIO UNITARIO</th><th>VALOR UNITARIO</th><th>VALOR PARCIAL</th>
</tr>
"""

if not materiales_df.empty:
    for _, row in materiales_df.iterrows():
        html += f"""
        <tr>
        <td>{row['DESCRIPCIÓN']}</td>
        <td colspan="2">{row['UNIDAD']}</td>
        <td colspan="2">{formato(row[f'CANTIDAD POR {unidad}'], 3)}</td>
        <td>{pesos(row['PRECIO UNITARIO'])}</td>
        <td>{pesos(row['VALOR UNITARIO'])}</td>
        <td>{pesos(row['VALOR PARCIAL'])}</td>
        </tr>
        """
else:
    html += """
    <tr><td colspan="8">No aplica material permanente para este APU.</td></tr>
    """

html += f"""
<tr><td colspan="7" class="subtotal">Sub-Total Materiales Unitario</td><td>{pesos(subtotal_materiales_unitario)}</td></tr>

<tr><td colspan="8" class="section">3. TRANSPORTE</td></tr>
<tr>
<th>ÍTEM</th><th>DISTANCIA</th><th>CANTIDAD</th><th>m³-km</th>
<th colspan="2">TARIFA</th><th colspan="2">VALOR PARCIAL</th>
</tr>
"""

if not transporte_df.empty:
    for _, row in transporte_df.iterrows():
        html += f"""
        <tr>
        <td>{row['ÍTEM']}</td>
        <td>{row['DISTANCIA (km)']}</td>
        <td>{formato(row['CANTIDAD (m³)'], 3)}</td>
        <td>{row['m³-km']}</td>
        <td colspan="2">{pesos(row['TARIFA'])}</td>
        <td colspan="2">{pesos(row['VALOR PARCIAL'])}</td>
        </tr>
        """
else:
    html += """
    <tr><td colspan="8">No aplica transporte directo.</td></tr>
    """

html += f"""
<tr><td colspan="7" class="subtotal">Sub-Total Transporte Unitario</td><td>{pesos(subtotal_transporte_unitario)}</td></tr>

<tr><td colspan="8" class="section">4. MANO DE OBRA</td></tr>
<tr>
<th>TRABAJADOR</th><th>CANTIDAD</th><th>JORNAL</th>
<th>PRESTACIONES</th><th>COSTO HORA</th>
<th>RENDIMIENTO</th><th>VALOR UNITARIO</th><th>VALOR PARCIAL</th>
</tr>
"""

for _, row in mano_df.iterrows():
    html += f"""
    <tr>
    <td>{row['TRABAJADOR']}</td>
    <td>{formato(row['CANTIDAD'], 2)}</td>
    <td>{pesos(row['JORNAL'])}</td>
    <td>{row['PRESTACIONES']}</td>
    <td>{pesos(row['COSTO HORA'])}</td>
    <td>{formato(row[f'RENDIMIENTO ({unidad}/h)'], 2)}</td>
    <td>{pesos(row['VALOR UNITARIO'])}</td>
    <td>{pesos(row['VALOR PARCIAL'])}</td>
    </tr>
    """

html += f"""
<tr><td colspan="7" class="subtotal">Sub-Total Mano de Obra Unitario</td><td>{pesos(subtotal_mano_unitario)}</td></tr>
<tr><td colspan="7" class="subtotal">Costo Directo Unitario</td><td>{pesos(costo_directo_unitario)}</td></tr>
<tr><td colspan="7" class="subtotal">AIU Unitario ({aiu_porcentaje}%)</td><td>{pesos(aiu_unitario)}</td></tr>
<tr class="total"><td colspan="7">VALOR UNITARIO TOTAL</td><td>{pesos(valor_unitario_total)}</td></tr>
<tr class="total"><td colspan="7">VALOR TOTAL DEL ÍTEM</td><td>{pesos(valor_total_apu)}</td></tr>
</table>
"""

st.markdown(html, unsafe_allow_html=True)

# =====================================================
# EXPORTAR CSV SIN OPENPYXL
# =====================================================

tabla_exportar = pd.DataFrame({
    "Concepto": [
        "Proyecto",
        "Integrantes",
        "Capítulo",
        "Ítem",
        "Unidad",
        "Cantidad de obra",
        "Subtotal equipo unitario",
        "Subtotal materiales unitario",
        "Subtotal transporte unitario",
        "Subtotal mano de obra unitario",
        "Costo directo unitario",
        "AIU unitario",
        "Valor unitario total",
        "Valor total del ítem",
        "Cumplimiento checklist (%)"
    ],
    "Valor": [
        proyecto,
        contrato,
        capitulo,
        item,
        unidad,
        cantidad_obra,
        subtotal_equipo_unitario,
        subtotal_materiales_unitario,
        subtotal_transporte_unitario,
        subtotal_mano_unitario,
        costo_directo_unitario,
        aiu_unitario,
        valor_unitario_total,
        valor_total_apu,
        cumplimiento
    ]
})

csv = descargar_csv(tabla_exportar)

st.download_button(
    label="📥 Descargar resumen del APU en CSV",
    data=csv,
    file_name=f"APU_{apu.replace(' ', '_')}.csv",
    mime="text/csv"
)low_html=True)
