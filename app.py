import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="APU Presupuestos",
    page_icon="📊",
    layout="wide"
)

# =====================================================
# DATOS GENERALES DEL SISTEMA
# =====================================================

JORNADA_HORAS = 8
PRECIO_GASOLINA = 10984
PRESTACIONES_SOCIALES = 1.65

# =====================================================
# BASE DE DATOS DE MAQUINARIA
# =====================================================

MAQUINARIA_DB = {
    "Retroexcavadora": {
        "tipo": "75 HP",
        "unidad": "m³",
        "tarifa_hora": 90000,
        "tiempo_min": 4.7,
        "capacidad_m3": 6.5,
        "consumo_gal_hora": 5.0,
    },
    "Volqueta": {
        "tipo": "6.5 m³",
        "unidad": "m³",
        "tarifa_hora": 75000,
        "tiempo_min": 4.7,
        "capacidad_m3": 6.5,
        "consumo_gal_hora": 4.0,
    },
    "Excavadora hidráulica": {
        "tipo": "120 HP",
        "unidad": "m³",
        "tarifa_hora": 180000,
        "tiempo_min": 3.5,
        "capacidad_m3": 1.0,
        "consumo_gal_hora": 6.5,
    },
    "Bulldozer": {
        "tipo": "D6",
        "unidad": "m³",
        "tarifa_hora": 160000,
        "tiempo_min": 5.5,
        "capacidad_m3": 8.0,
        "consumo_gal_hora": 7.0,
    },
    "Motoniveladora": {
        "tipo": "120 HP",
        "unidad": "m³",
        "tarifa_hora": 140000,
        "tiempo_min": 6.0,
        "capacidad_m3": 7.0,
        "consumo_gal_hora": 5.5,
    },
    "Cargador frontal": {
        "tipo": "2.5 m³",
        "unidad": "m³",
        "tarifa_hora": 130000,
        "tiempo_min": 4.0,
        "capacidad_m3": 2.5,
        "consumo_gal_hora": 5.8,
    },
    "Compactador": {
        "tipo": "Rodillo",
        "unidad": "m³",
        "tarifa_hora": 110000,
        "tiempo_min": 6.0,
        "capacidad_m3": 5.0,
        "consumo_gal_hora": 4.2,
    },
    "Motobomba": {
        "tipo": "-",
        "unidad": "DÍA",
        "tarifa_hora": 95000,
        "tiempo_min": 60,
        "capacidad_m3": 1,
        "consumo_gal_hora": 0,
    },
}

# =====================================================
# BASE DE DATOS MANO DE OBRA
# =====================================================

MANO_OBRA_DB = {
    "Oficial": 100000,
    "Ayudante": 71428.57,
    "Obrero": 70000,
    "Operador retroexcavadora": 115909.09,
    "Operador volqueta": 127272.73,
    "Operador excavadora": 145454.55,
    "Operador motobomba": 71428.57,
    "Topógrafo": 107142.86,
    "Cadenero": 83928.57,
    "Ingeniero residente": 250000,
    "Maestro de obra": 140000,
}

# =====================================================
# FUNCIONES
# =====================================================

def pesos(valor):
    return f"$ {float(valor):,.2f}"

def rendimiento_hora(tiempo_min, capacidad):
    if tiempo_min <= 0:
        return 0
    return (60 * capacidad) / tiempo_min

def rendimiento_dia(rh):
    return rh * JORNADA_HORAS

def formato(valor, decimales=2):
    try:
        return f"{float(valor):,.{decimales}f}"
    except:
        return valor

# =====================================================
# INTERFAZ
# =====================================================

st.title("📊 MATRIZ APU - SISTEMA DE PRESUPUESTOS")

st.sidebar.header("Menú de APU")

apu = st.sidebar.selectbox(
    "Seleccione el ítem",
    [
        "1.1 Excavación mecánica en tierra",
        "1.2 Excavación mecánica en arena",
        "1.3 Excavación en roca",
        "1.4 Excavación manual",
        "1.5 Entibado de tubería",
        "1.6 Tubería"
    ]
)

# =====================================================
# DATOS DEL PROYECTO
# =====================================================

st.subheader("DATOS DEL PROYECTO")

col1, col2 = st.columns(2)

with col1:
    proyecto = st.text_input(
        "Proyecto",
        "UNIVERSIDAD MILITAR NUEVA GRANADA INSTALACIÓN DE TUBERÍA"
    )
    contrato = st.text_input(
        "Contrato",
        "CAMILA GÓMEZ, CHAROL REMÍREZ"
    )
    anio = st.number_input("Año", value=2026)

with col2:
    capitulo = st.text_input("Capítulo", "INSTALACIÓN DE TUBERÍA")
    item = st.text_input("Ítem", apu)
    unidad = st.text_input("Unidad", "m³")

st.divider()

# =====================================================
# PARÁMETROS
# =====================================================

st.subheader("PARÁMETROS DE EXCAVACIÓN Y ENTIBADO")

col3, col4, col5 = st.columns(3)

with col3:
    base_menor = st.number_input("Base menor B1 (m)", value=1.8)
    base_mayor = st.number_input("Base mayor B2 (m)", value=2.8)

with col4:
    longitud_tramo = st.number_input("Longitud del tramo L (m)", value=50.0)
    profundidad = st.number_input("Profundidad / altura H (m)", value=1.5)

with col5:
    factor_expansion = st.number_input("Factor de expansión", value=1.25)
    rendimiento_excavacion = st.number_input("Rendimiento excavación (m³/h)", value=1.0)
    capacidad_volqueta_general = st.number_input("Capacidad volqueta general (m³)", value=6.5)

area_perfil = 0.5 * ((base_menor + base_mayor) * longitud_tramo + profundidad * profundidad)
area_entibado = area_perfil * 2
volumen_excavacion = ((area_perfil - profundidad * profundidad) * 1.1) + profundidad ** 3
volumen_expansion = volumen_excavacion * factor_expansion
viajes_volqueta = volumen_expansion / capacidad_volqueta_general if capacidad_volqueta_general > 0 else 0

parametros_df = pd.DataFrame({
    "PARÁMETRO": [
        "Área en perfil",
        "Área de entibado",
        "Volumen de excavación",
        "Volumen de expansión",
        "Viajes equivalentes de volqueta",
        "Rendimiento excavación"
    ],
    "VALOR": [
        area_perfil,
        area_entibado,
        volumen_excavacion,
        volumen_expansion,
        viajes_volqueta,
        rendimiento_excavacion
    ],
    "UNIDAD": [
        "m²",
        "m²",
        "m³",
        "m³",
        "viajes",
        "m³/h"
    ]
})

st.dataframe(parametros_df, use_container_width=True)

st.divider()

# =====================================================
# EQUIPO
# =====================================================

st.subheader("1. EQUIPO")

maquinas_seleccionadas = st.multiselect(
    "Seleccione maquinaria/equipos",
    list(MAQUINARIA_DB.keys()),
    default=["Retroexcavadora", "Volqueta"]
)

filas_equipo = []

for maquina in maquinas_seleccionadas:
    datos = MAQUINARIA_DB[maquina]

    st.markdown(f"### {maquina}")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        tarifa = st.number_input(
            f"Tarifa {maquina}",
            value=float(datos["tarifa_hora"]),
            key=f"tarifa_{maquina}"
        )

    with c2:
        tiempo_min = st.number_input(
            f"Tiempo ciclo {maquina} (min)",
            value=float(datos["tiempo_min"]),
            key=f"tiempo_{maquina}"
        )

    with c3:
        capacidad = st.number_input(
            f"Capacidad {maquina} (m³)",
            value=float(datos["capacidad_m3"]),
            key=f"capacidad_{maquina}"
        )

    with c4:
        cantidad_equipo = st.number_input(
            f"Cantidad de {maquina}",
            value=1.0,
            min_value=0.0,
            key=f"cantidad_equipo_{maquina}"
        )

    rh = rendimiento_hora(tiempo_min, capacidad)
    rd = rendimiento_dia(rh)

    if "manual" in apu.lower() or "entibado" in apu.lower():
        rendimiento_usado = rendimiento_excavacion * JORNADA_HORAS
    else:
        rendimiento_usado = rd

    valor_parcial = (
        cantidad_equipo * tarifa * JORNADA_HORAS
    ) / rendimiento_usado if rendimiento_usado > 0 else 0

    filas_equipo.append({
        "DESCRIPCIÓN": maquina.upper(),
        "TIPO": datos["tipo"],
        "UND": datos["unidad"],
        "CANTIDAD": cantidad_equipo,
        "TARIFA": tarifa,
        "RENDIMIENTO": rendimiento_usado,
        "VALOR PARCIAL": valor_parcial
    })

equipo_df = pd.DataFrame(filas_equipo)
subtotal_equipo = equipo_df["VALOR PARCIAL"].sum() if not equipo_df.empty else 0

st.dataframe(equipo_df, use_container_width=True)
st.success(f"Sub - Total Equipo: {pesos(subtotal_equipo)}")

st.divider()

# =====================================================
# MATERIALES
# =====================================================

st.subheader("2. MATERIALES DE OBRA")

filas_materiales = []

if "entibado" in apu.lower():
    materiales_entibado = {
        "Puntales (1x10\")": 59900,
        "Largueros (1x10\")": 59900,
        "Codales (2x3\")": 28900,
        "Puntilla cabeza 2-1/2\" 500g": 5100,
    }

    for material, precio_base in materiales_entibado.items():
        c1, c2 = st.columns(2)

        with c1:
            cantidad_mat = st.number_input(
                f"Cantidad {material}",
                value=1.0,
                min_value=0.0,
                key=f"cant_{material}"
            )

        with c2:
            precio_mat = st.number_input(
                f"Precio unitario {material}",
                value=float(precio_base),
                min_value=0.0,
                key=f"precio_{material}"
            )

        valor_material = cantidad_mat * precio_mat

        filas_materiales.append({
            "DESCRIPCIÓN": material.upper(),
            "UNIDAD": "GLOBAL",
            "PRECIO UNITARIO": precio_mat,
            "CANTIDAD": cantidad_mat,
            "VALOR PARCIAL": valor_material
        })

else:
    for maquina in maquinas_seleccionadas:
        datos = MAQUINARIA_DB[maquina]

        consumo = st.number_input(
            f"Consumo gasolina {maquina} (gal/h)",
            value=float(datos["consumo_gal_hora"]),
            min_value=0.0,
            key=f"consumo_{maquina}"
        )

        horas_reales = st.number_input(
            f"Horas reales de uso {maquina}",
            value=1.0,
            min_value=0.0,
            key=f"horas_{maquina}"
        )

        cantidad_gal = consumo * horas_reales
        valor_material = cantidad_gal * PRECIO_GASOLINA

        if consumo > 0:
            filas_materiales.append({
                "DESCRIPCIÓN": f"GASOLINA {maquina.upper()}",
                "UNIDAD": "GL",
                "PRECIO UNITARIO": PRECIO_GASOLINA,
                "CANTIDAD": cantidad_gal,
                "VALOR PARCIAL": valor_material
            })

materiales_df = pd.DataFrame(filas_materiales)
subtotal_materiales = materiales_df["VALOR PARCIAL"].sum() if not materiales_df.empty else 0

st.dataframe(materiales_df, use_container_width=True)
st.success(f"Sub - Total Materiales de obra: {pesos(subtotal_materiales)}")

st.divider()

# =====================================================
# TRANSPORTE
# =====================================================

st.subheader("3. TRANSPORTE")

distancia_botadero = st.number_input("Distancia al botadero (km)", value=15.0)
tarifa_transporte = st.number_input("Tarifa transporte ($/m³-km)", value=1500.0)
tarifa_vertimiento = st.number_input("Tarifa vertimiento / botadero ($/m³)", value=80000.0)

cantidad_transporte = st.number_input(
    "Cantidad transportada (m³)",
    value=float(volumen_expansion)
)

m3_km = distancia_botadero * cantidad_transporte
valor_transporte_material = m3_km * tarifa_transporte
valor_vertimiento = cantidad_transporte * tarifa_vertimiento
subtotal_transporte = valor_transporte_material + valor_vertimiento

transporte_df = pd.DataFrame({
    "ÍTEM": ["MATERIAL EXCAVADO", "BOTADERO"],
    "DISTANCIA": [distancia_botadero, ""],
    "CANTIDAD (m³)": [cantidad_transporte, cantidad_transporte],
    "m³-Km": [m3_km, ""],
    "TARIFA": [tarifa_transporte, tarifa_vertimiento],
    "VALOR PARCIAL": [valor_transporte_material, valor_vertimiento]
})

st.dataframe(transporte_df, use_container_width=True)
st.success(f"Sub - Total Transporte: {pesos(subtotal_transporte)}")

st.divider()

# =====================================================
# MANO DE OBRA
# =====================================================

st.subheader("4. MANO DE OBRA")

trabajadores_seleccionados = st.multiselect(
    "Seleccione trabajadores",
    list(MANO_OBRA_DB.keys()),
    default=["Oficial", "Ayudante", "Operador retroexcavadora"]
)

filas_mano = []

for trabajador in trabajadores_seleccionados:
    c1, c2 = st.columns(2)

    with c1:
        cantidad_trabajadores = st.number_input(
            f"Cantidad de {trabajador}",
            min_value=0.0,
            value=1.0,
            step=1.0,
            key=f"cantidad_trab_{trabajador}"
        )

    with c2:
        jornal = st.number_input(
            f"Jornal {trabajador}",
            min_value=0.0,
            value=float(MANO_OBRA_DB[trabajador]),
            step=1000.0,
            key=f"jornal_{trabajador}"
        )

    jornal_total = jornal * PRESTACIONES_SOCIALES
    rendimiento_mano_obra = rendimiento_excavacion * JORNADA_HORAS

    valor_mano = (
        cantidad_trabajadores * jornal_total
    ) / rendimiento_mano_obra if rendimiento_mano_obra > 0 else 0

    filas_mano.append({
        "TRABAJADOR": trabajador.upper(),
        "CANTIDAD": cantidad_trabajadores,
        "JORNAL": jornal,
        "PRESTACIONES": PRESTACIONES_SOCIALES,
        "JORNAL TOTAL": jornal_total,
        "RENDIMIENTO": rendimiento_mano_obra,
        "VALOR PARCIAL": valor_mano
    })

mano_df = pd.DataFrame(filas_mano)
subtotal_mano = mano_df["VALOR PARCIAL"].sum() if not mano_df.empty else 0

st.dataframe(mano_df, use_container_width=True)
st.success(f"Sub - Total Mano de obra: {pesos(subtotal_mano)}")

st.divider()

# =====================================================
# RESUMEN
# =====================================================

total_costos_directos = subtotal_equipo + subtotal_materiales + subtotal_transporte + subtotal_mano

st.metric("TOTAL COSTOS DIRECTOS", pesos(total_costos_directos))

# =====================================================
# TABLA FINAL TIPO EXCEL
# =====================================================

st.subheader("TABLA COMPLETA DEL APU")

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
    padding: 4px;
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
<tr><td colspan="7"><b>ANÁLISIS DE PRECIOS UNITARIOS APU</b></td></tr>
<tr><td>PROYECTO</td><td colspan="6">{proyecto}</td></tr>
<tr><td>CONTRATO</td><td colspan="6">{contrato}</td></tr>
<tr><td>AÑO</td><td colspan="6">{anio}</td></tr>
<tr><td>CAPÍTULO</td><td colspan="6">{capitulo}</td></tr>
<tr><td>ÍTEM</td><td colspan="6">{item}</td></tr>
<tr><td>UNIDAD</td><td colspan="6">{unidad}</td></tr>

<tr><td colspan="7" class="section">PARÁMETROS DE CÁLCULO</td></tr>
<tr><th>PARÁMETRO</th><th colspan="3">VALOR</th><th colspan="3">UNIDAD</th></tr>
"""

for _, row in parametros_df.iterrows():
    html += f"""
    <tr>
    <td>{row['PARÁMETRO']}</td>
    <td colspan="3">{formato(row['VALOR'], 3)}</td>
    <td colspan="3">{row['UNIDAD']}</td>
    </tr>
    """

html += """
<tr><td colspan="7" class="section">1. EQUIPO</td></tr>
<tr>
<th>DESCRIPCIÓN</th><th>TIPO</th><th>UND</th><th>CANTIDAD</th>
<th>TARIFA</th><th>RENDIMIENTO</th><th>VALOR PARCIAL</th>
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
    <td>{formato(row['RENDIMIENTO'], 2)}</td>
    <td>{pesos(row['VALOR PARCIAL'])}</td>
    </tr>
    """

html += f"""
<tr><td colspan="6" class="subtotal">Sub - Total Equipo</td><td>{pesos(subtotal_equipo)}</td></tr>

<tr><td colspan="7" class="section">2. MATERIALES DE OBRA</td></tr>
<tr>
<th>DESCRIPCIÓN</th><th colspan="2">UNIDAD</th><th>PRECIO UNITARIO</th>
<th>CANTIDAD</th><th colspan="2">VALOR PARCIAL</th>
</tr>
"""

for _, row in materiales_df.iterrows():
    html += f"""
    <tr>
    <td>{row['DESCRIPCIÓN']}</td>
    <td colspan="2">{row['UNIDAD']}</td>
    <td>{pesos(row['PRECIO UNITARIO'])}</td>
    <td>{formato(row['CANTIDAD'], 3)}</td>
    <td colspan="2">{pesos(row['VALOR PARCIAL'])}</td>
    </tr>
    """

html += f"""
<tr><td colspan="6" class="subtotal">Sub - Total Materiales de obra</td><td>{pesos(subtotal_materiales)}</td></tr>

<tr><td colspan="7" class="section">3. TRANSPORTE</td></tr>
<tr>
<th>ÍTEM</th><th>DISTANCIA</th><th>CANTIDAD</th><th>m³-Km</th>
<th>TARIFA</th><th colspan="2">VALOR PARCIAL</th>
</tr>
"""

for _, row in transporte_df.iterrows():
    html += f"""
    <tr>
    <td>{row['ÍTEM']}</td>
    <td>{row['DISTANCIA']}</td>
    <td>{row['CANTIDAD (m³)']}</td>
    <td>{row['m³-Km']}</td>
    <td>{pesos(row['TARIFA'])}</td>
    <td colspan="2">{pesos(row['VALOR PARCIAL'])}</td>
    </tr>
    """

html += f"""
<tr><td colspan="6" class="subtotal">Sub - Total Transporte</td><td>{pesos(subtotal_transporte)}</td></tr>

<tr><td colspan="7" class="section">4. MANO DE OBRA</td></tr>
<tr>
<th>TRABAJADOR</th><th>CANTIDAD</th><th>JORNAL</th>
<th>PRESTACIONES</th><th>JORNAL TOTAL</th>
<th>RENDIMIENTO</th><th>VALOR PARCIAL</th>
</tr>
"""

for _, row in mano_df.iterrows():
    html += f"""
    <tr>
    <td>{row['TRABAJADOR']}</td>
    <td>{formato(row['CANTIDAD'], 2)}</td>
    <td>{pesos(row['JORNAL'])}</td>
    <td>{row['PRESTACIONES']}</td>
    <td>{pesos(row['JORNAL TOTAL'])}</td>
    <td>{formato(row['RENDIMIENTO'], 2)}</td>
    <td>{pesos(row['VALOR PARCIAL'])}</td>
    </tr>
    """

html += f"""
<tr><td colspan="6" class="subtotal">Sub - Total Mano de obra</td><td>{pesos(subtotal_mano)}</td></tr>
<tr class="total"><td colspan="6">TOTAL COSTOS DIRECTOS</td><td>{pesos(total_costos_directos)}</td></tr>
</table>
"""

st.markdown(html, unsafe_allow_html=True)
