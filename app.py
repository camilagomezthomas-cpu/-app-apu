import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="APU Presupuestos",
    page_icon="📊",
    layout="wide"
)

JORNADA_HORAS = 8
PRESTACIONES_SOCIALES = 1.65
PRECIO_GASOLINA_DEFECTO = 10984.0

MANO_OBRA_DB = {
    "Oficial": 100000,
    "Ayudante": 71428.57,
    "Obrero": 70000,
    "Maestro de obra": 140000,
    "Operador retroexcavadora": 115909.09,
    "Operador volqueta": 127272.73,
    "Topógrafo": 107142.86,
    "Cadenero": 83928.57,
    "Auxiliar de ingeniería": 106115.45,
    "Soldador": 130000,
    "Armador": 110000,
}

EQUIPOS_DB = {
    "Retroexcavadora": {"tipo": "75 HP", "tarifa_hora": 90000, "tiempo_min": 4.7, "capacidad": 6.5, "consumo_gal_h": 5.0},
    "Volqueta": {"tipo": "6.5 m³", "tarifa_hora": 75000, "tiempo_min": 4.7, "capacidad": 6.5, "consumo_gal_h": 4.0},
    "Herramienta menor": {"tipo": "%", "tarifa_hora": 0, "tiempo_min": 0, "capacidad": 0, "consumo_gal_h": 0.0},
    "Mezcladora": {"tipo": "Concreto", "tarifa_hora": 60000, "tiempo_min": 24, "capacidad": 1.0, "consumo_gal_h": 0.0},
    "Vibrador de concreto": {"tipo": "Eléctrico", "tarifa_hora": 35000, "tiempo_min": 20, "capacidad": 1.0, "consumo_gal_h": 0.0},
    "Formaleta / herramienta menor": {"tipo": "Manual", "tarifa_hora": 25000, "tiempo_min": 6, "capacidad": 1.0, "consumo_gal_h": 0.0},
    "Soldadora": {"tipo": "Eléctrica", "tarifa_hora": 85000, "tiempo_min": 0.75, "capacidad": 1.0, "consumo_gal_h": 0.0},
    "Compactador manual": {"tipo": "Rana / canguro", "tarifa_hora": 45000, "tiempo_min": 5, "capacidad": 1.0, "consumo_gal_h": 0.8},
}

APUS = {
    "Excavación mecánica": {
        "unidad": "m³",
        "capitulo": "MOVIMIENTO DE TIERRAS",
        "equipos": ["Retroexcavadora", "Volqueta"],
        "mano": ["Operador retroexcavadora", "Operador volqueta", "Ayudante", "Topógrafo", "Cadenero"],
        "materiales": "gasolina",
        "checklist": [
            "Replanteo del área de excavación verificado",
            "Profundidad y ancho de excavación revisados",
            "Taludes o entibado revisados",
            "Material excavado retirado correctamente",
            "Botadero autorizado definido",
            "Uso de EPP verificado",
        ],
    },
    "Excavación manual": {
        "unidad": "m³",
        "capitulo": "MOVIMIENTO DE TIERRAS",
        "equipos": ["Herramienta menor"],
        "mano": ["Oficial", "Ayudante", "Auxiliar de ingeniería"],
        "materiales": {},
        "checklist": [
            "Replanteo realizado",
            "Profundidad verificada",
            "Ancho de excavación verificado",
            "Taludes revisados",
            "Material retirado correctamente",
            "Uso de EPP verificado",
        ],
    },
    "Zapata en concreto": {
        "unidad": "m³",
        "capitulo": "CIMENTACIÓN",
        "equipos": ["Mezcladora", "Vibrador de concreto"],
        "mano": ["Oficial", "Ayudante"],
        "materiales": {
            "Concreto": {"unidad": "m³", "cantidad": 1.05, "precio": 420000},
            "Acero de refuerzo": {"unidad": "kg", "cantidad": 85, "precio": 5200},
            "Alambre negro": {"unidad": "kg", "cantidad": 1.5, "precio": 8000},
        },
        "checklist": [
            "Excavación conforme a planos",
            "Solado verificado",
            "Acero colocado según diseño",
            "Formaleta revisada",
            "Concreto vibrado correctamente",
            "Curado inicial realizado",
        ],
    },
    "Viga en concreto": {
        "unidad": "m³",
        "capitulo": "ESTRUCTURA EN CONCRETO",
        "equipos": ["Vibrador de concreto", "Formaleta / herramienta menor"],
        "mano": ["Oficial", "Ayudante"],
        "materiales": {
            "Concreto": {"unidad": "m³", "cantidad": 1.05, "precio": 420000},
            "Acero de refuerzo": {"unidad": "kg", "cantidad": 95, "precio": 5200},
            "Formaleta": {"unidad": "m²", "cantidad": 6, "precio": 35000},
        },
        "checklist": [
            "Acero instalado según planos",
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
        "equipos": ["Vibrador de concreto", "Formaleta / herramienta menor"],
        "mano": ["Oficial", "Ayudante"],
        "materiales": {
            "Concreto": {"unidad": "m³", "cantidad": 0.12, "precio": 420000},
            "Acero de refuerzo": {"unidad": "kg", "cantidad": 12, "precio": 5200},
            "Aligerante / casetón": {"unidad": "und", "cantidad": 1, "precio": 18000},
        },
        "checklist": [
            "Formaleta instalada",
            "Aligerantes colocados",
            "Acero revisado",
            "Instalaciones embebidas verificadas",
            "Concreto vaciado y vibrado",
            "Curado realizado",
        ],
    },
    "Estructura metálica": {
        "unidad": "kg",
        "capitulo": "ESTRUCTURA METÁLICA",
        "equipos": ["Soldadora"],
        "mano": ["Soldador", "Ayudante"],
        "materiales": {
            "Acero estructural": {"unidad": "kg", "cantidad": 1.0, "precio": 7800},
            "Electrodos / soldadura": {"unidad": "kg", "cantidad": 0.03, "precio": 18000},
            "Pintura anticorrosiva": {"unidad": "gl", "cantidad": 0.01, "precio": 95000},
        },
        "checklist": [
            "Material metálico certificado",
            "Cortes revisados",
            "Soldadura inspeccionada",
            "Alineación verificada",
            "Pintura anticorrosiva aplicada",
            "Montaje seguro",
        ],
    },
    "Instalación de tubería": {
        "unidad": "m",
        "capitulo": "INSTALACIÓN DE TUBERÍA",
        "equipos": ["Compactador manual", "Formaleta / herramienta menor"],
        "mano": ["Oficial", "Ayudante", "Topógrafo", "Cadenero"],
        "materiales": {
            "Puntales (1x10\")": {"unidad": "GLOBAL", "cantidad": 0.597, "precio": 59900},
            "Largueros (1x10\")": {"unidad": "GLOBAL", "cantidad": 0.473, "precio": 59900},
            "Codales (2x3\")": {"unidad": "GLOBAL", "cantidad": 0.038, "precio": 28900},
            "Puntilla cabeza 2-1/2\" 500g": {"unidad": "GLOBAL", "cantidad": 0.034, "precio": 5100},
            "Alambre calibre 16": {"unidad": "GLOBAL", "cantidad": 0.021, "precio": 15400},
            "Tubería PVC / sanitaria": {"unidad": "m", "cantidad": 1.0, "precio": 65000},
            "Arena de cama": {"unidad": "m³", "cantidad": 0.08, "precio": 85000},
            "Material seleccionado de relleno": {"unidad": "m³", "cantidad": 0.12, "precio": 70000},
            "Pegante / accesorios": {"unidad": "GLOBAL", "cantidad": 0.05, "precio": 45000},
        },
        "checklist": [
            "Replanteo topográfico realizado",
            "Nivel de fondo de zanja verificado",
            "Cama de arena instalada",
            "Pendiente de tubería revisada",
            "Uniones instaladas correctamente",
            "Relleno y compactación verificados",
            "Registro fotográfico realizado",
            "Uso de EPP verificado",
        ],
    },
}

def pesos(valor):
    return f"$ {float(valor):,.2f}"

def formato(valor, decimales=2):
    try:
        return f"{float(valor):,.{decimales}f}"
    except:
        return valor

def rendimiento_hora_ciclo(tiempo_min, capacidad):
    if tiempo_min <= 0:
        return 0
    return (60 * capacidad) / tiempo_min

def rendimiento_dia(rh, jornada):
    return rh * jornada

def csv_download(df):
    return df.to_csv(index=False).encode("utf-8-sig")

st.title("📊 MATRIZ APU - SISTEMA DE PRESUPUESTOS DE OBRA CIVIL")
st.caption("Trabajo académico universitario - Análisis de Precios Unitarios")

apu = st.sidebar.selectbox("Seleccione el APU", list(APUS.keys()))
data_apu = APUS[apu]
unidad = data_apu["unidad"]

st.subheader("DATOS DEL PROYECTO")

col1, col2 = st.columns(2)

with col1:
    proyecto = st.text_input("Proyecto", "UNIVERSIDAD MILITAR NUEVA GRANADA - PRESUPUESTO DE OBRA CIVIL")
    integrantes = st.text_input("Integrantes", "CAMILA GÓMEZ - CHAROL RAMÍREZ")
    anio = st.number_input("Año", value=2026, step=1)

with col2:
    capitulo = st.text_input("Capítulo", data_apu["capitulo"])
    item = st.text_input("Ítem", apu)
    unidad = st.text_input("Unidad del APU", unidad)

st.divider()

st.subheader("1. PARÁMETROS DE CÁLCULO")

jornada = st.number_input("Jornada laboral (h/día)", value=float(JORNADA_HORAS), min_value=1.0)

if apu == "Excavación mecánica":
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        base_menor = st.number_input("Base menor B1 (m)", value=1.8, min_value=0.0)
    with c2:
        base_mayor = st.number_input("Base mayor B2 (m)", value=2.8, min_value=0.0)
    with c3:
        longitud = st.number_input("Longitud L (m)", value=50.0, min_value=0.0)
    with c4:
        profundidad = st.number_input("Profundidad H (m)", value=1.5, min_value=0.0)

    factor_expansion = st.number_input("Factor de expansión", value=1.25, min_value=1.0)

    area_perfil = ((base_menor + base_mayor) / 2) * profundidad
    volumen_excavacion = area_perfil * longitud
    volumen_expansion = volumen_excavacion * factor_expansion
    cantidad_obra = volumen_excavacion

elif apu == "Excavación manual":
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        excavacion_manual = st.number_input("Excavación manual (m³)", value=1.0, min_value=0.01)
    with c2:
        tiempo_excavacion = st.number_input("Tiempo de excavación (h)", value=3.0, min_value=0.01)
    with c3:
        llenado = st.number_input("Llenado (m³)", value=7.0, min_value=0.01)
    with c4:
        tiempo_llenado = st.number_input("Tiempo de llenado (h)", value=2.0, min_value=0.01)

    cantidad_obra = st.number_input("Cantidad total de obra (m³)", value=100.0, min_value=0.0)

    rendimiento_excavacion = excavacion_manual / tiempo_excavacion
    rendimiento_llenado = llenado / tiempo_llenado
    rendimiento_base = min(rendimiento_excavacion, rendimiento_llenado)
    rendimiento_manual_dia = rendimiento_base * jornada

    area_perfil = 0
    volumen_excavacion = cantidad_obra
    volumen_expansion = 0
    factor_expansion = 0

else:
    cantidad_obra = st.number_input(f"Cantidad de obra ({unidad})", value=100.0, min_value=0.0)
    area_perfil = 0
    volumen_excavacion = 0
    volumen_expansion = 0
    factor_expansion = 0

aiu_porcentaje = st.number_input("AIU (%)", value=25.0, min_value=0.0)

st.divider()

st.subheader("2. EQUIPO")

filas_equipo = []
rendimientos_equipo = {}

for equipo in data_apu["equipos"]:
    datos = EQUIPOS_DB[equipo]

    if equipo == "Herramienta menor":
        continue

    st.markdown(f"#### {equipo}")

    e1, e2, e3, e4 = st.columns(4)

    with e1:
        cantidad_equipo = st.number_input(f"Cantidad {equipo}", value=1.0, min_value=0.0, key=f"cant_equipo_{equipo}")
    with e2:
        tarifa_hora = st.number_input(f"Tarifa {equipo} ($/h)", value=float(datos["tarifa_hora"]), min_value=0.0, key=f"tarifa_{equipo}")
    with e3:
        tiempo_min = st.number_input(f"Tiempo ciclo {equipo} (min)", value=float(datos["tiempo_min"]), min_value=0.01, key=f"tiempo_{equipo}")
    with e4:
        capacidad = st.number_input(f"Capacidad {equipo} ({unidad})", value=float(datos["capacidad"]), min_value=0.01, key=f"capacidad_{equipo}")

    rh = rendimiento_hora_ciclo(tiempo_min, capacidad)
    rd = rendimiento_dia(rh, jornada)

    rendimientos_equipo[equipo] = rh

    valor_unitario = (cantidad_equipo * tarifa_hora) / rh if rh > 0 else 0

    filas_equipo.append({
        "DESCRIPCIÓN": equipo.upper(),
        "TIPO": datos["tipo"],
        "UND": "h",
        "CANTIDAD": cantidad_equipo,
        "TARIFA": tarifa_hora,
        "TIEMPO CICLO": tiempo_min,
        "CAPACIDAD": capacidad,
        "RENDIMIENTO HORA": rh,
        "RENDIMIENTO DÍA": rd,
        "VALOR UNITARIO": valor_unitario,
        "VALOR PARCIAL": valor_unitario * cantidad_obra
    })

equipo_df = pd.DataFrame(filas_equipo)
subtotal_equipo_unitario_sin_hm = equipo_df["VALOR UNITARIO"].sum() if not equipo_df.empty else 0

st.divider()

st.subheader("3. MATERIALES DE OBRA")

filas_materiales = []

if data_apu["materiales"] == "gasolina":
    precio_gasolina = st.number_input("Precio gasolina ($/gal)", value=PRECIO_GASOLINA_DEFECTO, min_value=0.0)

    for equipo in data_apu["equipos"]:
        if equipo == "Herramienta menor":
            continue

        consumo = st.number_input(
            f"Consumo gasolina {equipo} (gal/h)",
            value=float(EQUIPOS_DB[equipo]["consumo_gal_h"]),
            min_value=0.0,
            key=f"consumo_{equipo}"
        )

        rh = rendimientos_equipo.get(equipo, 1)
        cantidad_gal_por_unidad = consumo / rh if rh > 0 else 0
        valor_unitario = cantidad_gal_por_unidad * precio_gasolina

        if consumo > 0:
            filas_materiales.append({
                "DESCRIPCIÓN": f"GASOLINA {equipo.upper()}",
                "UNIDAD": "GL",
                f"CANTIDAD POR {unidad}": cantidad_gal_por_unidad,
                "PRECIO UNITARIO": precio_gasolina,
                "VALOR UNITARIO": valor_unitario,
                "VALOR PARCIAL": valor_unitario * cantidad_obra
            })

else:
    for material, datos in data_apu["materiales"].items():
        m1, m2 = st.columns(2)

        with m1:
            cantidad_mat = st.number_input(f"Cantidad {material} por {unidad}", value=float(datos["cantidad"]), min_value=0.0, key=f"cant_{material}")
        with m2:
            precio_mat = st.number_input(f"Precio unitario {material}", value=float(datos["precio"]), min_value=0.0, key=f"precio_{material}")

        valor_unitario = cantidad_mat * precio_mat

        filas_materiales.append({
            "DESCRIPCIÓN": material.upper(),
            "UNIDAD": datos["unidad"],
            f"CANTIDAD POR {unidad}": cantidad_mat,
            "PRECIO UNITARIO": precio_mat,
            "VALOR UNITARIO": valor_unitario,
            "VALOR PARCIAL": valor_unitario * cantidad_obra
        })

materiales_df = pd.DataFrame(filas_materiales)
subtotal_materiales_unitario = materiales_df["VALOR UNITARIO"].sum() if not materiales_df.empty else 0

st.divider()

st.subheader("4. TRANSPORTE")

filas_transporte = []

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
    valor_transporte = m3_km * tarifa_transporte
    valor_botadero = cantidad_transportada * tarifa_vertimiento

    filas_transporte.append({
        "ÍTEM": "MATERIAL EXCAVADO",
        "DISTANCIA": distancia_botadero,
        "CANTIDAD": cantidad_transportada,
        "M3_KM": m3_km,
        "TARIFA": tarifa_transporte,
        "VALOR PARCIAL": valor_transporte
    })

    filas_transporte.append({
        "ÍTEM": "BOTADERO",
        "DISTANCIA": "",
        "CANTIDAD": cantidad_transportada,
        "M3_KM": "",
        "TARIFA": tarifa_vertimiento,
        "VALOR PARCIAL": valor_botadero
    })

transporte_df = pd.DataFrame(filas_transporte)
subtotal_transporte_total = transporte_df["VALOR PARCIAL"].sum() if not transporte_df.empty else 0
subtotal_transporte_unitario = subtotal_transporte_total / cantidad_obra if cantidad_obra > 0 else 0

st.divider()

st.subheader("5. MANO DE OBRA Y CUADRILLA")

if apu == "Excavación manual":
    rendimiento_base_mano = rendimiento_base
else:
    rendimiento_base_mano = min([rendimientos_equipo[e] for e in rendimientos_equipo]) if rendimientos_equipo else 1

filas_mano = []

for trabajador in data_apu["mano"]:
    mo1, mo2 = st.columns(2)

    with mo1:
        cantidad_trabajadores = st.number_input(
            f"Cantidad {trabajador}",
            value=1.0,
            min_value=0.0,
            step=1.0,
            key=f"cant_{trabajador}"
        )
    with mo2:
        jornal = st.number_input(
            f"Jornal diario {trabajador}",
            value=float(MANO_OBRA_DB[trabajador]),
            min_value=0.0,
            step=1000.0,
            key=f"jornal_{trabajador}"
        )

    jornal_total = jornal * PRESTACIONES_SOCIALES
    costo_hora = jornal_total / jornada
    valor_unitario_mano = (cantidad_trabajadores * costo_hora) / rendimiento_base_mano if rendimiento_base_mano > 0 else 0

    filas_mano.append({
        "TRABAJADOR": trabajador.upper(),
        "CANTIDAD": cantidad_trabajadores,
        "JORNAL": jornal,
        "PRESTACIONES": PRESTACIONES_SOCIALES,
        "JORNAL TOTAL": jornal_total,
        "COSTO HORA": costo_hora,
        "RENDIMIENTO": rendimiento_base_mano,
        "VALOR UNITARIO": valor_unitario_mano,
        "VALOR PARCIAL": valor_unitario_mano * cantidad_obra
    })

mano_df = pd.DataFrame(filas_mano)
subtotal_mano_unitario = mano_df["VALOR UNITARIO"].sum() if not mano_df.empty else 0

st.divider()

st.subheader("6. HERRAMIENTA MENOR")

herramienta_menor_pct = st.number_input("Herramienta menor (%)", value=10.0, min_value=0.0)
valor_herramienta_menor_unitario = subtotal_mano_unitario * herramienta_menor_pct / 100

herramienta_df = pd.DataFrame([{
    "DESCRIPCIÓN": "HERRAMIENTA MENOR",
    "TIPO": "%",
    "UND": "%",
    "CANTIDAD": herramienta_menor_pct,
    "TARIFA": subtotal_mano_unitario,
    "TIEMPO CICLO": "",
    "CAPACIDAD": "",
    "RENDIMIENTO HORA": "",
    "RENDIMIENTO DÍA": "",
    "VALOR UNITARIO": valor_herramienta_menor_unitario,
    "VALOR PARCIAL": valor_herramienta_menor_unitario * cantidad_obra
}])

subtotal_equipo_unitario = subtotal_equipo_unitario_sin_hm + valor_herramienta_menor_unitario

st.divider()

st.subheader("7. LISTA DE CHEQUEO EN CAMPO")

checks = []
for punto in data_apu["checklist"]:
    checks.append(st.checkbox(punto))

cumplimiento = (sum(checks) / len(checks)) * 100 if checks else 0
st.progress(cumplimiento / 100)
st.info(f"Cumplimiento de lista de chequeo: {cumplimiento:.1f}%")

st.divider()

costo_directo_unitario = (
    subtotal_equipo_unitario +
    subtotal_materiales_unitario +
    subtotal_transporte_unitario +
    subtotal_mano_unitario
)

aiu_unitario = costo_directo_unitario * (aiu_porcentaje / 100)
valor_unitario_total = costo_directo_unitario + aiu_unitario
valor_total_item = valor_unitario_total * cantidad_obra

st.subheader("8. TABLAS INDIVIDUALES")

equipo_final_df = pd.concat([equipo_df, herramienta_df], ignore_index=True)

st.markdown("### Tabla Equipo")
st.dataframe(equipo_final_df, use_container_width=True)

st.markdown("### Tabla Materiales")
st.dataframe(materiales_df, use_container_width=True)

st.markdown("### Tabla Transporte")
st.dataframe(transporte_df, use_container_width=True)

st.markdown("### Tabla Mano de Obra")
st.dataframe(mano_df, use_container_width=True)

st.divider()

st.subheader("9. RESUMEN")

r1, r2, r3, r4 = st.columns(4)
r1.metric("Costo directo unitario", pesos(costo_directo_unitario))
r2.metric("AIU unitario", pesos(aiu_unitario))
r3.metric("Valor unitario total", pesos(valor_unitario_total))
r4.metric("Valor total del ítem", pesos(valor_total_item))

st.divider()

st.subheader("10. TABLA FINAL DEL PRESUPUESTO APU")

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
<tr><td colspan="11"><b>ANÁLISIS DE PRECIOS UNITARIOS APU</b></td></tr>
<tr><td>PROYECTO</td><td colspan="10">{proyecto}</td></tr>
<tr><td>INTEGRANTES</td><td colspan="10">{integrantes}</td></tr>
<tr><td>AÑO</td><td colspan="10">{anio}</td></tr>
<tr><td>CAPÍTULO</td><td colspan="10">{capitulo}</td></tr>
<tr><td>ÍTEM</td><td colspan="10">{item}</td></tr>
<tr><td>UNIDAD</td><td colspan="10">{unidad}</td></tr>
<tr><td>CANTIDAD DE OBRA</td><td colspan="10">{formato(cantidad_obra, 3)} {unidad}</td></tr>
"""

if apu == "Excavación mecánica":
    html += f"""
    <tr><td colspan="11" class="section">PARÁMETROS DE EXCAVACIÓN MECÁNICA</td></tr>
    <tr><td>Área perfil trapezoidal</td><td colspan="5">{formato(area_perfil, 3)}</td><td colspan="5">m²</td></tr>
    <tr><td>Volumen excavación banco</td><td colspan="5">{formato(volumen_excavacion, 3)}</td><td colspan="5">m³</td></tr>
    <tr><td>Factor expansión</td><td colspan="5">{formato(factor_expansion, 3)}</td><td colspan="5">-</td></tr>
    <tr><td>Volumen expansión transporte</td><td colspan="5">{formato(volumen_expansion, 3)}</td><td colspan="5">m³</td></tr>
    """

if apu == "Excavación manual":
    html += f"""
    <tr><td colspan="11" class="section">PARÁMETROS DE EXCAVACIÓN MANUAL</td></tr>
    <tr><td>Excavación</td><td colspan="5">{formato(excavacion_manual, 3)}</td><td colspan="5">m³</td></tr>
    <tr><td>Tiempo de excavación</td><td colspan="5">{formato(tiempo_excavacion, 3)}</td><td colspan="5">h</td></tr>
    <tr><td>Llenado</td><td colspan="5">{formato(llenado, 3)}</td><td colspan="5">m³</td></tr>
    <tr><td>Tiempo de llenado</td><td colspan="5">{formato(tiempo_llenado, 3)}</td><td colspan="5">h</td></tr>
    <tr><td>Rendimiento hora usado</td><td colspan="5">{formato(rendimiento_base, 3)}</td><td colspan="5">m³/h</td></tr>
    <tr><td>Rendimiento día</td><td colspan="5">{formato(rendimiento_manual_dia, 3)}</td><td colspan="5">m³/día</td></tr>
    """

html += """
<tr><td colspan="11" class="section">1. EQUIPO</td></tr>
<tr>
<th>DESCRIPCIÓN</th><th>TIPO</th><th>UND</th><th>CANT.</th>
<th>TARIFA</th><th>TIEMPO CICLO</th><th>CAPACIDAD</th>
<th>REND. HORA</th><th>REND. DÍA</th><th>V. UNITARIO</th><th>V. PARCIAL</th>
</tr>
"""

for _, row in equipo_final_df.iterrows():
    html += f"""
    <tr>
    <td>{row.get('DESCRIPCIÓN', '')}</td>
    <td>{row.get('TIPO', '')}</td>
    <td>{row.get('UND', '')}</td>
    <td>{formato(row.get('CANTIDAD', 0), 2)}</td>
    <td>{pesos(row.get('TARIFA', 0))}</td>
    <td>{row.get('TIEMPO CICLO', '')}</td>
    <td>{row.get('CAPACIDAD', '')}</td>
    <td>{row.get('RENDIMIENTO HORA', '')}</td>
    <td>{row.get('RENDIMIENTO DÍA', '')}</td>
    <td>{pesos(row.get('VALOR UNITARIO', 0))}</td>
    <td>{pesos(row.get('VALOR PARCIAL', 0))}</td>
    </tr>
    """

html += f"""
<tr><td colspan="10" class="subtotal">Sub - Total Equipo</td><td>{pesos(subtotal_equipo_unitario)}</td></tr>

<tr><td colspan="11" class="section">2. MATERIALES DE OBRA</td></tr>
<tr>
<th>DESCRIPCIÓN</th><th colspan="2">UNIDAD</th><th colspan="3">CANTIDAD</th>
<th colspan="2">PRECIO UNITARIO</th><th>VALOR UNITARIO</th><th colspan="2">VALOR PARCIAL</th>
</tr>
"""

if materiales_df.empty:
    html += """<tr><td colspan="11">No aplica materiales de obra.</td></tr>"""
else:
    for _, row in materiales_df.iterrows():
        html += f"""
        <tr>
        <td>{row['DESCRIPCIÓN']}</td>
        <td colspan="2">{row['UNIDAD']}</td>
        <td colspan="3">{formato(row[f'CANTIDAD POR {unidad}'], 4)}</td>
        <td colspan="2">{pesos(row['PRECIO UNITARIO'])}</td>
        <td>{pesos(row['VALOR UNITARIO'])}</td>
        <td colspan="2">{pesos(row['VALOR PARCIAL'])}</td>
        </tr>
        """

html += f"""
<tr><td colspan="10" class="subtotal">Sub - Total Materiales</td><td>{pesos(subtotal_materiales_unitario)}</td></tr>
"""

html += """
<tr><td colspan="11" class="section">3. TRANSPORTE</td></tr>
<tr>
<th>ÍTEM</th><th>DISTANCIA</th><th>CANTIDAD</th><th>m³-km</th>
<th colspan="3">TARIFA</th><th colspan="4">VALOR PARCIAL</th>
</tr>
"""

if transporte_df.empty:
    html += """<tr><td colspan="11">No aplica transporte directo.</td></tr>"""
else:
    for _, row in transporte_df.iterrows():
        html += f"""
        <tr>
        <td>{row['ÍTEM']}</td>
        <td>{row['DISTANCIA']}</td>
        <td>{formato(row['CANTIDAD'], 3)}</td>
        <td>{row['M3_KM']}</td>
        <td colspan="3">{pesos(row['TARIFA'])}</td>
        <td colspan="4">{pesos(row['VALOR PARCIAL'])}</td>
        </tr>
        """

html += f"""
<tr><td colspan="10" class="subtotal">Sub - Total Transporte</td><td>{pesos(subtotal_transporte_unitario)}</td></tr>

<tr><td colspan="11" class="section">4. MANO DE OBRA</td></tr>
<tr>
<th>TRABAJADOR</th><th>CANTIDAD</th><th>JORNAL</th><th>PRESTACIONES</th>
<th>JORNAL TOTAL</th><th>COSTO HORA</th><th>RENDIMIENTO</th>
<th colspan="2">VALOR UNITARIO</th><th colspan="2">VALOR PARCIAL</th>
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
    <td>{pesos(row['COSTO HORA'])}</td>
    <td>{formato(row['RENDIMIENTO'], 3)} {unidad}/h</td>
    <td colspan="2">{pesos(row['VALOR UNITARIO'])}</td>
    <td colspan="2">{pesos(row['VALOR PARCIAL'])}</td>
    </tr>
    """

html += f"""
<tr><td colspan="10" class="subtotal">Sub - Total Mano de obra</td><td>{pesos(subtotal_mano_unitario)}</td></tr>
<tr><td colspan="10" class="subtotal">Costo Directo Unitario</td><td>{pesos(costo_directo_unitario)}</td></tr>
<tr><td colspan="10" class="subtotal">AIU Unitario ({aiu_porcentaje}%)</td><td>{pesos(aiu_unitario)}</td></tr>
<tr class="total"><td colspan="10">VALOR UNITARIO TOTAL</td><td>{pesos(valor_unitario_total)}</td></tr>
<tr class="total"><td colspan="10">VALOR TOTAL DEL ÍTEM</td><td>{pesos(valor_total_item)}</td></tr>
</table>
"""

st.markdown(html, unsafe_allow_html=True)

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
        integrantes,
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
        valor_total_item,
        cumplimiento
    ]
})

csv = csv_download(tabla_exportar)

st.download_button(
    label="📥 Descargar resumen del APU en CSV",
    data=csv,
    file_name=f"APU_{apu.replace(' ', '_')}.csv",
    mime="text/csv"
)
