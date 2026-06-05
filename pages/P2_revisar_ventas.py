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
# CONVERTIR COLUMNAS NUMÉRICAS
# --------------------------------------------------

df_ventas["subtotal"] = pd.to_numeric(
    df_ventas["subtotal"],
    errors="coerce"
)

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

with col1:

    lista_años = sorted(
        df_ventas["año"]
        .dropna()
        .unique()
        .tolist()
    )

    año = st.selectbox(
        "Año",
        lista_años
    )

with col2:

    lista_meses = sorted(
        df_ventas[
            df_ventas["año"] == año
        ]["mes"]
        .dropna()
        .unique()
        .tolist()
    )

    mes = st.selectbox(
        "Mes",
        lista_meses
    )

with col3:

    lista_dias = sorted(
        df_ventas[
            (df_ventas["año"] == año)
            &
            (df_ventas["mes"] == mes)
        ]["dia"]
        .dropna()
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

df_filtrado = df_ventas[
    (df_ventas["año"] == año)
    &
    (df_ventas["mes"] == mes)
    &
    (df_ventas["dia"] == dia)
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
# TABLA
# --------------------------------------------------

st.divider()

st.header("Ventas encontradas")

st.dataframe(
    df_filtrado,
    use_container_width=True,
    hide_index=True
)