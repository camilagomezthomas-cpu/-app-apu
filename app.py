import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="APU Presupuestos Obra Civil",
    page_icon="📊",
    layout="wide"
)

# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================

JORNADA_HORAS = 8
PRESTACIONES_SOCIALES = 1.65

def pesos(valor):
    return f"$ {float(valor):,.2f}"

def formato(valor, decimales=2):
    return f"{float(valor):,.{decimales}f}"

def rendimiento_hora(capacidad, tiempo_min):
    if tiempo_min <= 0:
        return 0
    return (60 * capacidad) / tiempo_min

# =========================================================
# BASE DE DATOS
# =========================================================

MANO_OBRA = {
    "Oficial": 100000,
    "Ayudante": 71428.57,
    "Operador retroexcavadora": 120000,
    "Operador volqueta": 120000,
    "Topógrafo": 150000,
    "Cadenero": 90000,
    "Auxiliar de ingeniería": 130000,
}

# =========================================================
# TITULO
# =========================================================

st.title("📊 SISTEMA APU - OBRA CIVIL")
st.subheader("Análisis de Precios Unitarios")

# =========================================================
# DATOS PROYECTO
# =========================================================

st.header("1. DATOS DEL PROYECTO")

c1, c2 = st.columns(2)

with c1:
    proyecto = st.text_input(
        "Proyecto",
        "PRESUPUESTO DE OBRA CIVIL"
    )

    integrantes = st.text_input(
        "Integrantes",
        "CAMILA GÓMEZ - CHAROL RAMÍREZ"
    )

with c2:
    capitulo = st.text_input(
        "Capítulo",
        "MOVIMIENTO DE TIERRAS"
    )

    item = st.selectbox(
        "Seleccione actividad",
        [
            "Excavación mecánica",
            "Excavación manual",
            "Zapata",
            "Viga",
            "Losa aligerada",
            "Estructura metálica",
            "Instalación de tubería"
        ]
    )

# =========================================================
# PARÁMETROS
# =========================================================

st.header("2. PARÁMETROS")

col1, col2, col3, col4 = st.columns(4)

with col1:
    cantidad_obra = st.number_input(
        "Cantidad de obra",
        value=100.0
    )

with col2:
    unidad_obra = st.selectbox(
        "Unidad",
        ["m³", "m²", "kg", "m"]
    )

with col3:
    jornada = st.number_input(
        "Jornada (h)",
        value=8.0
    )

with col4:
    aiu = st.number_input(
        "AIU (%)",
        value=25.0
    )

# =========================================================
# EQUIPO
# =========================================================

st.header("3. EQUIPO")

filas_equipo = []

usar_retro = st.checkbox("Usar retroexcavadora", value=True)
usar_volqueta = st.checkbox("Usar volqueta", value=True)

rendimiento_base = 1

if usar_retro:

    st.subheader("Retroexcavadora")

    e1, e2, e3, e4 = st.columns(4)

    with e1:
        tarifa_retro = st.number_input(
            "Tarifa retroexcavadora ($/h)",
            value=90000.0
        )

    with e2:
        capacidad_retro = st.number_input(
            "Capacidad retroexcavadora",
            value=6.5
        )

    with e3:
        tiempo_retro = st.number_input(
            "Tiempo ciclo retro (min)",
            value=4.7
        )

    with e4:
        cantidad_retro = st.number_input(
            "Cantidad retro",
            value=1.0
        )

    rendimiento_retro = rendimiento_hora(
        capacidad_retro,
        tiempo_retro
    )

    rendimiento_base = rendimiento_retro

    valor_unitario_retro = (
        cantidad_retro * tarifa_retro
    ) / rendimiento_retro

    filas_equipo.append({
        "DESCRIPCIÓN": "RETROEXCAVADORA",
        "UND": "h",
        "TARIFA": tarifa_retro,
        "RENDIMIENTO": rendimiento_retro,
        "VALOR UNITARIO": valor_unitario_retro,
        "VALOR PARCIAL": valor_unitario_retro * cantidad_obra
    })

if usar_volqueta:

    st.subheader("Volqueta")

    v1, v2, v3, v4 = st.columns(4)

    with v1:
        tarifa_volqueta = st.number_input(
            "Tarifa volqueta ($/h)",
            value=75000.0
        )

    with v2:
        capacidad_volqueta = st.number_input(
            "Capacidad volqueta",
            value=6.5
        )

    with v3:
        tiempo_volqueta = st.number_input(
            "Tiempo ciclo volqueta (min)",
            value=4.7
        )

    with v4:
        cantidad_volqueta = st.number_input(
            "Cantidad volqueta",
            value=1.0
        )

    rendimiento_volqueta = rendimiento_hora(
        capacidad_volqueta,
        tiempo_volqueta
    )

    rendimiento_base = min(
        rendimiento_base,
        rendimiento_volqueta
    )

    valor_unitario_volqueta = (
        cantidad_volqueta * tarifa_volqueta
    ) / rendimiento_volqueta

    filas_equipo.append({
        "DESCRIPCIÓN": "VOLQUETA",
        "UND": "h",
        "TARIFA": tarifa_volqueta,
        "RENDIMIENTO": rendimiento_volqueta,
        "VALOR UNITARIO": valor_unitario_volqueta,
        "VALOR PARCIAL": valor_unitario_volqueta * cantidad_obra
    })

equipo_df = pd.DataFrame(filas_equipo)

subtotal_equipo = (
    equipo_df["VALOR UNITARIO"].sum()
    if not equipo_df.empty else 0
)

# =========================================================
# MATERIALES
# =========================================================

st.header("4. MATERIALES")

filas_materiales = []

st.subheader("Materiales base")

material_base = st.checkbox(
    "Agregar concreto",
    value=False
)

if material_base:

    m1, m2 = st.columns(2)

    with m1:
        cantidad_concreto = st.number_input(
            "Cantidad concreto",
            value=1.0
        )

    with m2:
        precio_concreto = st.number_input(
            "Precio concreto",
            value=420000.0
        )

    valor_concreto = (
        cantidad_concreto * precio_concreto
    )

    filas_materiales.append({
        "DESCRIPCIÓN": "CONCRETO",
        "UNIDAD": "m³",
        "CANTIDAD": cantidad_concreto,
        "PRECIO UNITARIO": precio_concreto,
        "VALOR UNITARIO": valor_concreto,
        "VALOR PARCIAL": valor_concreto * cantidad_obra
    })

# =========================================================
# MATERIALES ADICIONALES
# =========================================================

st.subheader("Agregar materiales adicionales")

activar_materiales = st.checkbox(
    "Agregar materiales adicionales"
)

if activar_materiales:

    numero_materiales = st.number_input(
        "Cantidad de materiales",
        value=1,
        min_value=1,
        step=1
    )

    for i in range(int(numero_materiales)):

        st.markdown(f"### Material {i+1}")

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            nombre = st.text_input(
                f"Nombre material {i+1}",
                value="Grava",
                key=f"nombre_{i}"
            )

        with c2:
            unidad_material = st.text_input(
                f"Unidad material {i+1}",
                value="m³",
                key=f"unidad_{i}"
            )

        with c3:
            cantidad_material = st.number_input(
                f"Cantidad material {i+1}",
                value=1.0,
                key=f"cantidad_{i}"
            )

        with c4:
            precio_material = st.number_input(
                f"Precio material {i+1}",
                value=0.0,
                key=f"precio_{i}"
            )

        valor_material = (
            cantidad_material * precio_material
        )

        filas_materiales.append({
            "DESCRIPCIÓN": nombre.upper(),
            "UNIDAD": unidad_material,
            "CANTIDAD": cantidad_material,
            "PRECIO UNITARIO": precio_material,
            "VALOR UNITARIO": valor_material,
            "VALOR PARCIAL": valor_material * cantidad_obra
        })

materiales_df = pd.DataFrame(filas_materiales)

subtotal_materiales = (
    materiales_df["VALOR UNITARIO"].sum()
    if not materiales_df.empty else 0
)

# =========================================================
# TRANSPORTE
# =========================================================

st.header("5. TRANSPORTE")

t1, t2, t3 = st.columns(3)

with t1:
    distancia = st.number_input(
        "Distancia botadero (km)",
        value=15.0
    )

with t2:
    tarifa_transporte = st.number_input(
        "Tarifa transporte ($/m³-km)",
        value=1500.0
    )

with t3:
    tarifa_botadero = st.number_input(
        "Tarifa botadero ($/m³)",
        value=80000.0
    )

m3_km = cantidad_obra * distancia

valor_transporte = (
    m3_km * tarifa_transporte
)

valor_botadero = (
    cantidad_obra * tarifa_botadero
)

transporte_df = pd.DataFrame([
    {
        "ÍTEM": "MATERIAL EXCAVADO",
        "DISTANCIA": distancia,
        "CANTIDAD": cantidad_obra,
        "m³-km": m3_km,
        "TARIFA": tarifa_transporte,
        "VALOR PARCIAL": valor_transporte
    },
    {
        "ÍTEM": "BOTADERO",
        "DISTANCIA": "",
        "CANTIDAD": cantidad_obra,
        "m³-km": "",
        "TARIFA": tarifa_botadero,
        "VALOR PARCIAL": valor_botadero
    }
])

subtotal_transporte = (
    valor_transporte + valor_botadero
) / cantidad_obra

# =========================================================
# MANO DE OBRA
# =========================================================

st.header("6. MANO DE OBRA")

filas_mano = []

for trabajador, jornal_base in MANO_OBRA.items():

    usar = st.checkbox(
        f"Usar {trabajador}",
        value=False,
        key=f"usar_{trabajador}"
    )

    if usar:

        c1, c2 = st.columns(2)

        with c1:
            cantidad_personal = st.number_input(
                f"Cantidad {trabajador}",
                value=1.0,
                key=f"cantidad_{trabajador}"
            )

        with c2:
            jornal = st.number_input(
                f"Jornal {trabajador}",
                value=float(jornal_base),
                key=f"jornal_{trabajador}"
            )

        jornal_total = (
            jornal * PRESTACIONES_SOCIALES
        )

        costo_hora = (
            jornal_total / jornada
        )

        valor_unitario = (
            cantidad_personal * costo_hora
        ) / rendimiento_base

        filas_mano.append({
            "TRABAJADOR": trabajador,
            "CANTIDAD": cantidad_personal,
            "JORNAL": jornal,
            "PRESTACIONES": PRESTACIONES_SOCIALES,
            "JORNAL TOTAL": jornal_total,
            "COSTO HORA": costo_hora,
            "RENDIMIENTO": rendimiento_base,
            "VALOR UNITARIO": valor_unitario,
            "VALOR PARCIAL": valor_unitario * cantidad_obra
        })

mano_df = pd.DataFrame(filas_mano)

subtotal_mano = (
    mano_df["VALOR UNITARIO"].sum()
    if not mano_df.empty else 0
)

# =========================================================
# HERRAMIENTA MENOR
# =========================================================

st.header("7. HERRAMIENTA MENOR")

herramienta_pct = st.number_input(
    "Herramienta menor (%)",
    value=10.0
)

herramienta_valor = (
    subtotal_mano * herramienta_pct / 100
)

# =========================================================
# CHECKLIST
# =========================================================

st.header("8. LISTA DE CHEQUEO")

checks = [
    st.checkbox("Replanteo realizado"),
    st.checkbox("Uso de EPP"),
    st.checkbox("Nivelación verificada"),
    st.checkbox("Materiales revisados"),
    st.checkbox("Control de calidad realizado"),
]

cumplimiento = (
    sum(checks) / len(checks)
) * 100

st.progress(cumplimiento / 100)

# =========================================================
# COSTOS
# =========================================================

st.header("9. RESUMEN")

costo_directo = (
    subtotal_equipo +
    subtotal_materiales +
    subtotal_transporte +
    subtotal_mano +
    herramienta_valor
)

aiu_valor = (
    costo_directo * aiu / 100
)

valor_unitario_total = (
    costo_directo + aiu_valor
)

valor_total = (
    valor_unitario_total * cantidad_obra
)

# =========================================================
# TABLAS
# =========================================================

st.subheader("TABLA EQUIPO")
st.dataframe(equipo_df)

st.subheader("TABLA MATERIALES")
st.dataframe(materiales_df)

st.subheader("TABLA TRANSPORTE")
st.dataframe(transporte_df)

st.subheader("TABLA MANO DE OBRA")
st.dataframe(mano_df)

# =========================================================
# RESUMEN FINAL
# =========================================================

st.subheader("RESULTADOS")

r1, r2, r3, r4 = st.columns(4)

r1.metric(
    "Costo directo",
    pesos(costo_directo)
)

r2.metric(
    "AIU",
    pesos(aiu_valor)
)

r3.metric(
    "Valor unitario",
    pesos(valor_unitario_total)
)

r4.metric(
    "Valor total",
    pesos(valor_total)
)

# =========================================================
# EXPORTAR CSV
# =========================================================

st.header("10. EXPORTAR")

resumen_df = pd.DataFrame({
    "Concepto": [
        "Proyecto",
        "Actividad",
        "Costo Directo",
        "AIU",
        "Valor Unitario",
        "Valor Total",
        "Cumplimiento Checklist"
    ],
    "Valor": [
        proyecto,
        item,
        costo_directo,
        aiu_valor,
        valor_unitario_total,
        valor_total,
        cumplimiento
    ]
})

csv = resumen_df.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    "📥 Descargar CSV",
    csv,
    "apu_presupuesto.csv",
    "text/csv"
)
