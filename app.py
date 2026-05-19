import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="APU Movimiento de Tierras",
    page_icon="📊",
    layout="wide"
)

JORNADA_HORAS = 8
PRECIO_GASOLINA = 10984
PRESTACIONES_SOCIALES = 1.65

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
    "Motobomba": {
        "tipo": "-",
        "unidad": "DIA",
        "tarifa_hora": 95000,
        "tiempo_min": 60,
        "capacidad_m3": 1,
        "consumo_gal_hora": 0,
    }
}

MANO_OBRA_DB = {
    "Oficial": 100000,
    "Ayudante": 71428.57,
    "Operador retroexcavadora": 115909.09,
    "Operador volqueta": 127272.73,
    "Operador motobomba": 71428.57,
    "Topógrafo": 107142.86,
    "Cadenero": 83928.57,
    "Obrero": 70000,
    "Ingeniero residente": 250000,
}

def pesos(valor):
    return f"$ {valor:,.2f}"

def rendimiento_hora(tiempo_min, capacidad):
    if tiempo_min <= 0:
        return 0
    return (60 * capacidad) / tiempo_min

def rendimiento_dia(rh):
    return rh * JORNADA_HORAS

st.title("📊 MATRIZ APU - SISTEMA DE PRESUPUESTOS")

st.sidebar.header("Menú de APU")
apu = st.sidebar.selectbox(
    "Seleccione el ítem",
    [
        "1.1 Excavación mecánica en tierra",
        "1.2 Excavación mecánica en arena",
        "1.3 Excavación en roca",
        "1.4 Excavación manual",
        "2. Entibado",
        "3. Tubería"
    ]
)

st.subheader("DATOS DEL PROYECTO")

col1, col2 = st.columns(2)

with col1:
    proyecto = st.text_input("Proyecto", "UNIVERSIDAD MILITAR NUEVA GRANADA INSTALACIÓN DE TUBERÍA")
    contrato = st.text_input("Contrato", "CONTRATO QUINO SANTIAGO, SANDOVAL JOSE, TORRES NICOLAS, ZARATE YAMID")
    anio = st.number_input("Año", value=2026)

with col2:
    capitulo = st.text_input("Capítulo", "INSTALACIÓN DE TUBERÍA")
    item = st.text_input("Ítem", apu)
    unidad = st.text_input("Unidad", "m³")

st.divider()

st.subheader("PARÁMETROS DE CÁLCULO")

col3, col4, col5 = st.columns(3)

with col3:
    base_menor = st.number_input("Base menor excavación (m)", value=1.8)
    base_mayor = st.number_input("Base mayor excavación (m)", value=2.8)
    longitud = st.number_input("Longitud del tramo (m)", value=50.0)

with col4:
    profundidad = st.number_input("Profundidad / altura (m)", value=1.5)
    factor_expansion = st.number_input("Factor de expansión", value=1.25)
    capacidad_volqueta = st.number_input("Capacidad volqueta (m³)", value=6.5)

with col5:
    rendimiento_excavacion = st.number_input("Rendimiento dado (m³/h)", value=1.0)
    distancia_botadero = st.number_input("Distancia al botadero (km)", value=15.0)
    tarifa_transporte = st.number_input("Tarifa transporte ($/m³-km)", value=1500.0)
    tarifa_vertimiento = st.number_input("Tarifa vertimiento / botadero ($/m³)", value=80000.0)

area_perfil = 0.5 * ((base_menor + base_mayor) * longitud + profundidad * profundidad)
area_entibado = area_perfil * 2
volumen_excavacion = ((area_perfil - profundidad * profundidad) * 1.1) + profundidad ** 3
volumen_expansion = volumen_excavacion * factor_expansion
viajes_volqueta = volumen_expansion / capacidad_volqueta if capacidad_volqueta > 0 else 0

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

    if "Excavación manual" in apu:
        rendimiento_usado = rendimiento_excavacion * JORNADA_HORAS
    else:
        rendimiento_usado = rd

    valor_parcial = (cantidad_equipo * tarifa * JORNADA_HORAS) / rendimiento_usado if rendimiento_usado > 0 else 0

    filas_equipo.append({
        "DESCRIPCIÓN": maquina.upper(),
        "TIPO": datos["tipo"],
        "UND": datos["unidad"],
        "CANTIDAD": cantidad_equipo,
        "TARIFA": tarifa,
        "TIEMPO MIN": tiempo_min,
        "CAPACIDAD": capacidad,
        "RENDIMIENTO HORA": rh,
        "RENDIMIENTO": rendimiento_usado,
        "VALOR PARCIAL": valor_parcial
    })

equipo_df = pd.DataFrame(filas_equipo)
subtotal_equipo = equipo_df["VALOR PARCIAL"].sum() if not equipo_df.empty else 0

st.dataframe(equipo_df, use_container_width=True)
st.success(f"Sub - Total Equipo: {pesos(subtotal_equipo)}")

st.divider()

st.subheader("2. MATERIALES DE OBRA")

filas_materiales = []

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

st.subheader("3. TRANSPORTE")

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
        "PRESTACIONES SOCIALES": PRESTACIONES_SOCIALES,
        "JORNAL TOTAL": jornal_total,
        "RENDIMIENTO": rendimiento_mano_obra,
        "VALOR PARCIAL": valor_mano
    })

mano_df = pd.DataFrame(filas_mano)
subtotal_mano = mano_df["VALOR PARCIAL"].sum() if not mano_df.empty else 0

st.dataframe(mano_df, use_container_width=True)
st.success(f"Sub - Total Mano de obra: {pesos(subtotal_mano)}")

st.divider()

total_costos_directos = (
    subtotal_equipo +
    subtotal_materiales +
    subtotal_transporte +
    subtotal_mano
)

resumen_df = pd.DataFrame({
    "CONCEPTO": [
        "Sub - Total Equipo",
        "Sub - Total Materiales de obra",
        "Sub - Total Transporte",
        "Sub - Total Mano de obra",
        "TOTAL COSTOS DIRECTOS"
    ],
    "VALOR": [
        subtotal_equipo,
        subtotal_materiales,
        subtotal_transporte,
        subtotal_mano,
        total_costos_directos
    ]
})

st.subheader("RESUMEN FINAL")
st.dataframe(resumen_df, use_container_width=True)

st.metric(
    "TOTAL COSTOS DIRECTOS",
    pesos(total_costos_directos)
)

st.divider()

st.subheader("TABLA COMPLETA DEL APU")

tabla_completa = pd.concat(
    [
        pd.DataFrame({"SECCIÓN": ["PARÁMETROS"] * len(parametros_df)}).join(parametros_df),
        pd.DataFrame({"SECCIÓN": ["EQUIPO"] * len(equipo_df)}).join(equipo_df),
        pd.DataFrame({"SECCIÓN": ["MATERIALES"] * len(materiales_df)}).join(materiales_df),
        pd.DataFrame({"SECCIÓN": ["TRANSPORTE"] * len(transporte_df)}).join(transporte_df),
        pd.DataFrame({"SECCIÓN": ["MANO DE OBRA"] * len(mano_df)}).join(mano_df),
        pd.DataFrame({"SECCIÓN": ["RESUMEN"] * len(resumen_df)}).join(resumen_df)
    ],
    ignore_index=True,
    sort=False
)

st.dataframe(tabla_completa, use_container_width=True)

csv = tabla_completa.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Descargar tabla completa en CSV",
    data=csv,
    file_name="apu_completo.csv",
    mime="text/csv"
)
