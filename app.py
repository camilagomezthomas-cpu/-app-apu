import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(
    page_title="DINAMO APU",
    page_icon="📊",
    layout="wide"
)

# =========================================================
# FUNCIONES
# =========================================================

def pesos(valor):
    return f"$ {valor:,.2f}"

def calcular_apu(
    cantidad,
    rendimiento,
    tarifa_hora,
    distancia,
    tarifa_transporte,
    tarifa_botadero,
    porcentaje_aiu
):

    if rendimiento <= 0:
        rendimiento = 1

    horas = cantidad / rendimiento

    costo_equipo = horas * tarifa_hora

    m3km = cantidad * distancia

    costo_transporte = m3km * tarifa_transporte

    costo_botadero = cantidad * tarifa_botadero

    costos_directos = (
        costo_equipo +
        costo_transporte +
        costo_botadero
    )

    aiu = costos_directos * (porcentaje_aiu / 100)

    total = costos_directos + aiu

    return {
        "Horas": horas,
        "Costo Equipo": costo_equipo,
        "m3km": m3km,
        "Costo Transporte": costo_transporte,
        "Costo Botadero": costo_botadero,
        "Costos Directos": costos_directos,
        "AIU": aiu,
        "TOTAL": total
    }

# =========================================================
# TITULO
# =========================================================

st.title("📊 DINAMO APU")
st.subheader("Sistema de Presupuestos de Obra Civil")

# =========================================================
# MENU
# =========================================================

tipo_apu = st.sidebar.selectbox(
    "Seleccione el APU",
    [
        "Excavación",
        "Zapata",
        "Vigas",
        "Losa Aligerada",
        "Estructura Metálica"
    ]
)

# =========================================================
# DATOS GENERALES
# =========================================================

st.header("1. DATOS GENERALES")

col1, col2 = st.columns(2)

with col1:
    proyecto = st.text_input(
        "Proyecto",
        "Proyecto de Construcción"
    )

    responsable = st.text_input(
        "Responsable",
        "Ingeniero Residente"
    )

with col2:
    unidad = st.selectbox(
        "Unidad",
        ["m³", "m²", "kg"]
    )

    porcentaje_aiu = st.number_input(
        "AIU (%)",
        value=25.0
    )

# =========================================================
# PARAMETROS
# =========================================================

st.header("2. PARÁMETROS")

col3, col4, col5 = st.columns(3)

with col3:

    cantidad = st.number_input(
        f"Cantidad ({unidad})",
        value=100.0
    )

    rendimiento = st.number_input(
        f"Rendimiento ({unidad}/h)",
        value=8.0
    )

with col4:

    tarifa_hora = st.number_input(
        "Tarifa Equipo ($/h)",
        value=120000.0
    )

    distancia = st.number_input(
        "Distancia Botadero (km)",
        value=15.0
    )

with col5:

    tarifa_transporte = st.number_input(
        "Tarifa Transporte ($/m³-km)",
        value=1500.0
    )

    tarifa_botadero = st.number_input(
        "Tarifa Botadero ($/m³)",
        value=80000.0
    )

# =========================================================
# CALCULOS
# =========================================================

resultado = calcular_apu(
    cantidad,
    rendimiento,
    tarifa_hora,
    distancia,
    tarifa_transporte,
    tarifa_botadero,
    porcentaje_aiu
)

# =========================================================
# RESULTADOS
# =========================================================

st.header("3. RESULTADOS DEL APU")

col6, col7, col8 = st.columns(3)

with col6:

    st.metric(
        "Horas Requeridas",
        f"{resultado['Horas']:.2f} h"
    )

    st.metric(
        "Costo Equipo",
        pesos(resultado["Costo Equipo"])
    )

with col7:

    st.metric(
        "Costo Transporte",
        pesos(resultado["Costo Transporte"])
    )

    st.metric(
        "Costo Botadero",
        pesos(resultado["Costo Botadero"])
    )

with col8:

    st.metric(
        "AIU",
        pesos(resultado["AIU"])
    )

    st.metric(
        "TOTAL APU",
        pesos(resultado["TOTAL"])
    )

# =========================================================
# TABLA
# =========================================================

st.header("4. TABLA RESUMEN")

tabla = pd.DataFrame({
    "CONCEPTO": [
        "Cantidad",
        "Rendimiento",
        "Horas",
        "Costo Equipo",
        "m3-km",
        "Costo Transporte",
        "Costo Botadero",
        "Costos Directos",
        "AIU",
        "TOTAL"
    ],
    "VALOR": [
        cantidad,
        rendimiento,
        resultado["Horas"],
        resultado["Costo Equipo"],
        resultado["m3km"],
        resultado["Costo Transporte"],
        resultado["Costo Botadero"],
        resultado["Costos Directos"],
        resultado["AIU"],
        resultado["TOTAL"]
    ]
})

st.dataframe(
    tabla,
    use_container_width=True
)

# =========================================================
# CHECKLIST
# =========================================================

st.header("5. LISTA DE CHEQUEO")

check1 = st.checkbox("Replanteo verificado")
check2 = st.checkbox("Profundidad revisada")
check3 = st.checkbox("Uso de EPP")
check4 = st.checkbox("Botadero aprobado")
check5 = st.checkbox("Cantidades verificadas")

# =========================================================
# EXPORTAR EXCEL
# =========================================================

st.header("6. EXPORTAR")

output = BytesIO()

with pd.ExcelWriter(output, engine='openpyxl') as writer:

    tabla.to_excel(
        writer,
        index=False,
        sheet_name='APU'
    )

excel_data = output.getvalue()

st.download_button(
    label="📥 Descargar Excel",
    data=excel_data,
    file_name="APU_DINAMO.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# =========================================================
# FOOTER
# =========================================================

st.success("Sistema APU funcionando correctamente ✅")
