import streamlit as st
import pandas as pd

# --------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------

st.set_page_config(
    page_title="REVISAR VENTAS",
    page_icon="📋",
    layout="wide"
)

st.title("📋 REVISAR VENTAS")

# --------------------------------------------------
# CARGAR VENTAS
# --------------------------------------------------

df_ventas = pd.read_csv(
    "tablas/ventas_df.csv",
    sep=";"
)

# --------------------------------------------------
# LIMPIAR NOMBRES DE COLUMNAS
# --------------------------------------------------

df_ventas.columns = df_ventas.columns.str.strip()

# --------------------------------------------------
# LIMPIAR VALORES NUMÉRICOS
# --------------------------------------------------

df_ventas["subtotal"] = (
    df_ventas["subtotal"]
    .astype(str)
    .str.replace(".", "", regex=False)
)

df_ventas["subtotal"] = pd.to_numeric(
    df_ventas["subtotal"],
    errors="coerce"
)

# --------------------------------------------------
# ASEGURAR TIPOS NUMÉRICOS
# --------------------------------------------------

df_ventas["año"] = pd.to_numeric(
    df_ventas["año"],
    errors="coerce"
)

df_ventas["mes"] = pd.to_numeric(
    df_ventas["mes"],
    errors="coerce"
)

df_ventas["dia"] = pd.to_numeric(
    df_ventas["dia"],
    errors="coerce"
)

# --------------------------------------------------
# FILTROS
# --------------------------------------------------

st.header("Filtros")

col1, col2, col3 = st.columns(3)

# ----------------------
# AÑO
# ----------------------

with col1:

    lista_años = ["Todos"] + sorted(
        df_ventas["año"]
        .dropna()
        .astype(int)
        .unique()
        .tolist()
    )

    año = st.selectbox(
        "Año",
        lista_años
    )

# ----------------------
# MES
# ----------------------

with col2:

    if año == "Todos":

        df_aux = df_ventas.copy()

    else:

        df_aux = df_ventas[
            df_ventas["año"] == año
        ]

    lista_meses = ["Todos"] + sorted(
        df_aux["mes"]
        .dropna()
        .astype(int)
        .unique()
        .tolist()
    )

    mes = st.selectbox(
        "Mes",
        lista_meses
    )

# ----------------------
# DÍA
# ----------------------

with col3:

    df_aux2 = df_aux.copy()

    if mes != "Todos":

        df_aux2 = df_aux2[
            df_aux2["mes"] == mes
        ]

    lista_dias = ["Todos"] + sorted(
        df_aux2["dia"]
        .dropna()
        .astype(int)
        .unique()
        .tolist()
    )

    dia = st.selectbox(
        "Día",
        lista_dias
    )

# --------------------------------------------------
# FILTRAR DATAFRAME
# --------------------------------------------------

df_filtrado = df_ventas.copy()

if año != "Todos":

    df_filtrado = df_filtrado[
        df_filtrado["año"] == año
    ]

if mes != "Todos":

    df_filtrado = df_filtrado[
        df_filtrado["mes"] == mes
    ]

if dia != "Todos":

    df_filtrado = df_filtrado[
        df_filtrado["dia"] == dia
    ]

# --------------------------------------------------
# MÉTRICAS
# --------------------------------------------------

st.divider()

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "Ventas encontradas",
        len(df_filtrado)
    )

with col2:

    st.metric(
        "Valor total",
        f"${df_filtrado['subtotal'].sum():,.0f}"
    )

# --------------------------------------------------
# COLUMNAS A OCULTAR
# --------------------------------------------------

columnas_ocultar = [
    "dia",
    "mes",
    "año",
    "colegio",
    "articulo",
    "talla",
    "hombro",
    "talle",
    "cintura",
    "largo",
    "Clasificación_antiguo",
    "Método de pago_antiguo"
]

df_mostrar = df_filtrado.drop(
    columns=columnas_ocultar,
    errors="ignore"
)

# --------------------------------------------------
# TABLA
# --------------------------------------------------

st.divider()

st.header("Ventas encontradas")

st.dataframe(
    df_mostrar,
    use_container_width=True,
    hide_index=True
)