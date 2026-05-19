import streamlit as st
import pandas as pd

# =====================================================

# CONFIGURACIÓN GENERAL

# =====================================================

st.set_page_config(
page_title="APU Movimiento de Tierras",
page_icon="📊",
layout="wide"
)

# =====================================================

# VARIABLES DEL SISTEMA

# =====================================================

JORNADA_HORAS = 8
PRECIO_GASOLINA = 10984
PRESTACIONES_SOCIALES = 1.65

# =====================================================

# BASE DE DATOS

# =====================================================

MAQUINARIA_DB = {
"Retroexcavadora": {
"tipo": "75 HP",
"unidad": "m³",
"tarifa_hora": 90000,
"tiempo_min": 4.7,
"capacidad_m3": 6.5,
"consumo_gal_hora": 2.5,
},

```
"Volqueta": {
    "tipo": "6.5 m³",
    "unidad": "m³",
    "tarifa_hora": 75000,
    "tiempo_min": 4.7,
    "capacidad_m3": 6.5,
    "consumo_gal_hora": 1.8,
}
```

}

MANO_OBRA_DB = {
"Operador retroexcavadora": {
"jornal": 115909.09,
},

```
"Operador volqueta": {
    "jornal": 127272.73,
}
```

}

# =====================================================

# FUNCIONES

# =====================================================

def calcular_rendimiento_hora(tiempo_min, capacidad_m3):
return (60 * capacidad_m3) / tiempo_min

def calcular_rendimiento_dia(rendimiento_hora):
return rendimiento_hora * JORNADA_HORAS

def formato_pesos(valor):
return f"$ {valor:,.2f}"

# =====================================================

# TÍTULO

# =====================================================

st.title("📊 MATRIZ APU - MOVIMIENTO DE TIERRAS")

# =====================================================

# DATOS GENERALES

# =====================================================

st.subheader("DATOS DEL PROYECTO")

col1, col2 = st.columns(2)

with col1:

```
proyecto = st.text_input(
    "Proyecto",
    "UNIVERSIDAD MILITAR NUEVA GRANADA"
)

contrato = st.text_input(
    "Contrato",
    "CONTRATO MOVIMIENTO DE TIERRAS"
)
```

with col2:

```
item = st.text_input(
    "Ítem",
    "1.1 EXCAVACIÓN MECÁNICA"
)

unidad = st.text_input(
    "Unidad",
    "m³"
)
```

st.divider()

# =====================================================

# EQUIPO

# =====================================================

st.subheader("1. EQUIPO")

maquinaria = st.selectbox(
"Seleccione maquinaria",
list(MAQUINARIA_DB.keys())
)

datos = MAQUINARIA_DB[maquinaria]

col3, col4, col5 = st.columns(3)

with col3:

```
tiempo_min = st.number_input(
    "Tiempo ciclo (min)",
    value=float(datos["tiempo_min"])
)
```

with col4:

```
capacidad_m3 = st.number_input(
    "Capacidad volqueta (m³)",
    value=float(datos["capacidad_m3"])
)
```

with col5:

```
tarifa = st.number_input(
    "Tarifa hora",
    value=float(datos["tarifa_hora"])
)
```

# =====================================================

# RENDIMIENTOS

# =====================================================

rendimiento_hora = calcular_rendimiento_hora(
tiempo_min,
capacidad_m3
)

rendimiento_dia = calcular_rendimiento_dia(
rendimiento_hora
)

valor_equipo = (
tarifa * JORNADA_HORAS
) / rendimiento_dia

equipo_df = pd.DataFrame({

```
"DESCRIPCIÓN": [maquinaria],
"TIPO": [datos["tipo"]],
"UND": [datos["unidad"]],
"TARIFA": [tarifa],
"RENDIMIENTO HORA": [rendimiento_hora],
"RENDIMIENTO DÍA": [rendimiento_dia],
"VALOR PARCIAL": [valor_equipo]
```

})

st.dataframe(
equipo_df,
use_container_width=True
)

st.success(
f"Sub - Total Equipo: {formato_pesos(valor_equipo)}"
)

# =====================================================

# MATERIALES

# =====================================================

st.subheader("2. MATERIALES DE OBRA")

horas_trabajo = st.number_input(
"Horas de trabajo",
value=1.0
)

consumo = datos["consumo_gal_hora"]

cantidad_gal = consumo * horas_trabajo

valor_materiales = cantidad_gal * PRECIO_GASOLINA

materiales_df = pd.DataFrame({

```
"DESCRIPCIÓN": [f"GASOLINA {maquinaria}"],
"UNIDAD": ["GL"],
"PRECIO UNITARIO": [PRECIO_GASOLINA],
"CANTIDAD": [cantidad_gal],
"VALOR PARCIAL": [valor_materiales]
```

})

st.dataframe(
materiales_df,
use_container_width=True
)

st.success(
f"Sub - Total Materiales: {formato_pesos(valor_materiales)}"
)

# =====================================================

# TRANSPORTE

# =====================================================

st.subheader("3. TRANSPORTE")

col6, col7 = st.columns(2)

with col6:

```
distancia = st.number_input(
    "Distancia (km)",
    value=1.90
)

cantidad = st.number_input(
    "Cantidad m³",
    value=1.2615
)
```

with col7:

```
tarifa_tierra = st.number_input(
    "Tarifa tierra",
    value=1700.0
)

tarifa_botadero = st.number_input(
    "Tarifa botadero",
    value=41538.46
)
```

m3_km = distancia * cantidad

valor_tierra = m3_km * tarifa_tierra

valor_botadero = cantidad * tarifa_botadero

valor_transporte = (
valor_tierra +
valor_botadero
)

transporte_df = pd.DataFrame({

```
"ÍTEM": ["TIERRA", "BOTADERO"],

"DISTANCIA": [
    distancia,
    ""
],

"CANTIDAD": [
    cantidad,
    cantidad
],

"TARIFA": [
    tarifa_tierra,
    tarifa_botadero
],

"VALOR PARCIAL": [
    valor_tierra,
    valor_botadero
]
```

})

st.dataframe(
transporte_df,
use_container_width=True
)

st.success(
f"Sub - Total Transporte: {formato_pesos(valor_transporte)}"
)

# =====================================================

# MANO DE OBRA

# =====================================================

st.subheader("4. MANO DE OBRA")

trabajador = st.selectbox(
"Trabajador",
list(MANO_OBRA_DB.keys())
)

jornal = MANO_OBRA_DB[trabajador]["jornal"]

jornal_total = jornal * PRESTACIONES_SOCIALES

valor_mano_obra = (
jornal_total / rendimiento_dia
)

mano_df = pd.DataFrame({

```
"TRABAJADOR": [trabajador],

"JORNAL": [jornal],

"PRESTACIONES": [PRESTACIONES_SOCIALES],

"JORNAL TOTAL": [jornal_total],

"RENDIMIENTO": [rendimiento_dia],

"VALOR PARCIAL": [valor_mano_obra]
```

})

st.dataframe(
mano_df,
use_container_width=True
)

st.success(
f"Sub - Total Mano de Obra: {formato_pesos(valor_mano_obra)}"
)

# =====================================================

# TOTAL

# =====================================================

total = (

```
valor_equipo +
valor_materiales +
valor_transporte +
valor_mano_obra
```

)

st.metric(
"TOTAL COSTOS DIRECTOS",
formato_pesos(total)
)
