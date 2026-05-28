import streamlit as st
import pandas as pd
from io import StringIO

st.set_page_config(
    page_title="APU Presupuestos",
    page_icon="📊",
    layout="wide"
)

# =========================
# FUNCIONES
# =========================

def pesos(valor):
    try:
        return f"$ {float(valor):,.2f}"
    except:
        return "$ 0.00"

def calcular_costo_por_rendimiento(costo_hora, rendimiento_hora):
    if rendimiento_hora <= 0:
        return 0
    return costo_hora / rendimiento_hora

def convertir_csv(df):
    return df.to_csv(index=False).encode("utf-8-sig")

# =========================
# ENCABEZADO
# =========================

st.title("📊 DINAMO APU - PRESUPUESTOS DE OBRA CIVIL")

st.markdown("""
Sistema para generar APUS de obra civil con rendimiento, equipos, mano de obra,
materiales, transporte, AIU y lista de chequeo en campo.
""")

# =========================
# MENÚ
# =========================

apu = st.sidebar.selectbox(
    "Seleccione el APU",
    [
        "Excavación mecánica",
        "Zapata en concreto",
        "Viga en concreto",
        "Losa aligerada",
        "Estructura metálica"
    ]
)

st.sidebar.success("APU seleccionado: " + apu)

# =========================
# DATOS GENERALES
# =========================

st.header("1. DATOS GENERALES DEL PROYECTO")

col1, col2, col3 = st.columns(3)

with col1:
    proyecto = st.text_input("Proyecto", "DINAMO APU")
    responsable = st.text_input("Responsable", "Camila Gómez - Charol Ramírez")

with col2:
    ubicacion = st.text_input("Ubicación", "Colombia")
    fecha = st.date_input("Fecha")

with col3:
    aiu_porcentaje = st.number_input("AIU (%)", value=25.0, min_value=0.0)
    cantidad_obra = st.number_input("Cantidad de obra", value=100.0, min_value=0.0)

# =========================
# CONFIGURACIÓN SEGÚN APU
# =========================

if apu == "Excavación mecánica":
    unidad = "m³"
    rendimiento_default = 8.0
    equipo_default = "Retroexcavadora"
    tarifa_default = 120000.0
    checklist = [
        "Replanteo verificado",
        "Profundidad de excavación revisada",
        "Taludes o entibado revisado",
        "Material excavado retirado correctamente",
        "Botadero autorizado",
        "Uso de EPP verificado"
    ]

elif apu == "Zapata en concreto":
    unidad = "m³"
    rendimiento_default = 2.5
    equipo_default = "Mezcladora / vibrador"
    tarifa_default = 70000.0
    checklist = [
        "Excavación conforme a planos",
        "Solado instalado",
        "Acero colocado según diseño",
        "Formaleta revisada",
        "Concreto vibrado",
        "Curado realizado"
    ]

elif apu == "Viga en concreto":
    unidad = "m³"
    rendimiento_default = 2.0
    equipo_default = "Vibrador de concreto"
    tarifa_default = 60000.0
    checklist = [
        "Acero de refuerzo instalado",
        "Formaleta nivelada",
        "Separadores colocados",
        "Concreto vaciado correctamente",
        "Vibrado realizado",
        "Curado verificado"
    ]

elif apu == "Losa aligerada":
    unidad = "m²"
    rendimiento_default = 12.0
    equipo_default = "Equipo menor"
    tarifa_default = 50000.0
    checklist = [
        "Formaleta instalada",
        "Casetones o aligerantes colocados",
        "Acero revisado",
        "Instalaciones embebidas revisadas",
        "Concreto vaciado",
        "Curado realizado"
    ]

else:
    unidad = "kg"
    rendimiento_default = 80.0
    equipo_default = "Soldadora / herramienta menor"
    tarifa_default = 85000.0
    checklist = [
        "Material certificado",
        "Cortes revisados",
        "Soldadura inspeccionada",
        "Alineación verificada",
        "Pintura anticorrosiva aplicada",
        "Montaje seguro"
    ]

# =========================
# PARÁMETROS DEL APU
# =========================

st.header("2. PARÁMETROS DEL APU")

col4, col5, col6 = st.columns(3)

with col4:
    st.subheader("Cantidad y rendimiento")
    cantidad = st.number_input(f"Cantidad ({unidad})", value=cantidad_obra, min_value=0.0)
    rendimiento = st.number_input(f"Rendimiento ({unidad}/hora)", value=rendimiento_default, min_value=0.01)

with col5:
    st.subheader("Equipo")
    equipo = st.text_input("Equipo principal", equipo_default)
    tarifa_equipo_hora = st.number_input("Tarifa equipo ($/hora)", value=tarifa_default, min_value=0.0)

with col6:
    st.subheader("Mano de obra")
    cuadrilla = st.text_input("Cuadrilla", "1 oficial + 1 ayudante")
    costo_mano_hora = st.number_input("Costo mano de obra ($/hora)", value=65000.0, min_value=0.0)

# =========================
# MATERIALES
# =========================

st.header("3. MATERIALES")

col7, col8, col9 = st.columns(3)

with col7:
    material_1 = st.text_input("Material 1", "Material principal")
    cantidad_mat_1 = st.number_input("Cantidad material 1", value=1.0, min_value=0.0)
    precio_mat_1 = st.number_input("Precio material 1", value=50000.0, min_value=0.0)

with col8:
    material_2 = st.text_input("Material 2", "Material secundario")
    cantidad_mat_2 = st.number_input("Cantidad material 2", value=1.0, min_value=0.0)
    precio_mat_2 = st.number_input("Precio material 2", value=25000.0, min_value=0.0)

with col9:
    material_3 = st.text_input("Material 3", "Herramienta menor")
    cantidad_mat_3 = st.number_input("Cantidad material 3", value=1.0, min_value=0.0)
    precio_mat_3 = st.number_input("Precio material 3", value=10000.0, min_value=0.0)

subtotal_materiales = (
    cantidad_mat_1 * precio_mat_1 +
    cantidad_mat_2 * precio_mat_2 +
    cantidad_mat_3 * precio_mat_3
)

# =========================
# TRANSPORTE
# =========================

st.header("4. TRANSPORTE")

col10, col11, col12 = st.columns(3)

with col10:
    distancia_botadero = st.number_input("Distancia al botadero (km)", value=15.0, min_value=0.0)

with col11:
    tarifa_transporte = st.number_input("Tarifa transporte ($/m³-km)", value=1500.0, min_value=0.0)

with col12:
    tarifa_botadero = st.number_input("Tarifa botadero ($/m³)", value=80000.0, min_value=0.0)

if unidad == "m³":
    cantidad_transportada = cantidad
else:
    cantidad_transportada = 0

m3_km = cantidad_transportada * distancia_botadero
costo_transporte = m3_km * tarifa_transporte
costo_botadero = cantidad_transportada * tarifa_botadero
subtotal_transporte = costo_transporte + costo_botadero

# =========================
# CÁLCULOS
# =========================

horas_requeridas = cantidad / rendimiento if rendimiento > 0 else 0

subtotal_equipo = horas_requeridas * tarifa_equipo_hora
subtotal_mano_obra = horas_requeridas * costo_mano_hora

costo_directo = (
    subtotal_equipo +
    subtotal_mano_obra +
    subtotal_materiales +
    subtotal_transporte
)

aiu_valor = costo_directo * (aiu_porcentaje / 100)
total_apu = costo_directo + aiu_valor

valor_unitario = total_apu / cantidad if cantidad > 0 else 0

# =========================
# RESULTADOS
# =========================

st.header("5. RESULTADOS")

r1, r2, r3, r4 = st.columns(4)

r1.metric("Horas requeridas", f"{horas_requeridas:.2f} h")
r2.metric("Costo directo", pesos(costo_directo))
r3.metric("AIU", pesos(aiu_valor))
r4.metric("Valor unitario", pesos(valor_unitario))

st.success(f"TOTAL DEL APU: {pesos(total_apu)}")

# =========================
# TABLAS
# =========================

st.header("6. TABLA DEL APU")

tabla_apu = pd.DataFrame({
    "CAPÍTULO": [
        "Equipo",
        "Mano de obra",
        "Materiales",
        "Transporte",
        "AIU",
        "Total"
    ],
    "DESCRIPCIÓN": [
        equipo,
        cuadrilla,
        "Materiales principales",
        "Transporte y botadero",
        f"AIU {aiu_porcentaje}%",
        "Total APU"
    ],
    "UNIDAD": [
        "hora",
        "hora",
        "global",
        "m³-km",
        "%",
        unidad
    ],
    "CANTIDAD": [
        horas_requeridas,
        horas_requeridas,
        1,
        m3_km,
        aiu_porcentaje,
        cantidad
    ],
    "VALOR PARCIAL": [
        subtotal_equipo,
        subtotal_mano_obra,
        subtotal_materiales,
        subtotal_transporte,
        aiu_valor,
        total_apu
    ]
})

st.dataframe(tabla_apu, use_container_width=True)

# =========================
# CHECKLIST
# =========================

st.header("7. LISTA DE CHEQUEO EN CAMPO")

checks = []

for item in checklist:
    checks.append(st.checkbox(item))

cumplimiento = (sum(checks) / len(checks)) * 100 if len(checks) > 0 else 0

st.progress(cumplimiento / 100)
st.info(f"Cumplimiento de checklist: {cumplimiento:.1f}%")

# =========================
# EXPORTAR SIN OPENPYXL
# =========================

st.header("8. EXPORTAR")

csv = convertir_csv(tabla_apu)

st.download_button(
    label="📥 Descargar APU en CSV",
    data=csv,
    file_name=f"APU_{apu.replace(' ', '_')}.csv",
    mime="text/csv"
)

# =========================
# NOTA FINAL
# =========================

st.success("Aplicación APU funcionando correctamente.")
