import streamlit as st
import pandas as pd

# --------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------

st.set_page_config(
    page_title="MONITOR INVENTARIO",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Monitor de Inventario")

# --------------------------------------------------
# CARGAR INVENTARIO
# --------------------------------------------------

df_inventario = pd.read_csv(
    "tablas/inventario.csv",
    sep=";"
)

# --------------------------------------------------
# LIMPIAR COLUMNAS
# --------------------------------------------------

df_inventario.columns = (
    df_inventario.columns
    .str.strip()
)

# --------------------------------------------------
# ASEGURAR INVENTARIO NUMÉRICO
# --------------------------------------------------

df_inventario["INVENTARIO"] = pd.to_numeric(
    df_inventario["INVENTARIO"],
    errors="coerce"
).fillna(0)

# --------------------------------------------------
# FILTROS
# --------------------------------------------------

st.header("Filtros")

col1, col2, col3 = st.columns(3)

# COLEGIO

with col1:

    lista_colegios = sorted(
        df_inventario["colegio"]
        .dropna()
        .unique()
        .tolist()
    )

    colegios = st.multiselect(
        "Colegio",
        lista_colegios,
        default=lista_colegios
    )

# ARTÍCULO

with col2:

    df_temp = df_inventario

    if len(colegios) > 0:

        df_temp = df_temp[
            df_temp["colegio"].isin(colegios)
        ]

    lista_articulos = sorted(
        df_temp["PRODUCTO"]
        .dropna()
        .unique()
        .tolist()
    )

    articulos = st.multiselect(
        "Artículo",
        lista_articulos,
        default=lista_articulos
    )

# TALLA

with col3:

    df_temp2 = df_temp

    if len(articulos) > 0:

        df_temp2 = df_temp2[
            df_temp2["PRODUCTO"].isin(articulos)
        ]

    lista_tallas = sorted(
        df_temp2["TALLA"]
        .dropna()
        .unique()
        .tolist()
    )

    tallas = st.multiselect(
        "Talla",
        lista_tallas,
        default=lista_tallas
    )

# --------------------------------------------------
# FILTRAR INVENTARIO
# --------------------------------------------------

df_filtrado = df_inventario.copy()

if len(colegios) > 0:

    df_filtrado = df_filtrado[
        df_filtrado["colegio"].isin(colegios)
    ]

if len(articulos) > 0:

    df_filtrado = df_filtrado[
        df_filtrado["PRODUCTO"].isin(articulos)
    ]

if len(tallas) > 0:

    df_filtrado = df_filtrado[
        df_filtrado["TALLA"].isin(tallas)
    ]

# --------------------------------------------------
# MÉTRICAS
# --------------------------------------------------

sin_stock = len(
    df_filtrado[
        df_filtrado["INVENTARIO"] <= 0
    ]
)

stock_bajo = len(
    df_filtrado[
        (df_filtrado["INVENTARIO"] > 0)
        &
        (df_filtrado["INVENTARIO"] <= 5)
    ]
)

stock_normal = len(
    df_filtrado[
        df_filtrado["INVENTARIO"] > 5
    ]
)

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "📦 Total Referencias",
        len(df_filtrado)
    )

with col2:

    st.metric(
        "🔴 Sin Stock",
        sin_stock
    )

with col3:

    st.metric(
        "🟡 Stock Bajo",
        stock_bajo
    )

with col4:

    st.metric(
        "🟢 Stock Normal",
        stock_normal
    )

# --------------------------------------------------
# SEMÁFORO INVENTARIO
# --------------------------------------------------

def color_inventario(valor):

    if valor <= 0:

        return (
            "background-color:#ff4b4b;"
            "color:white;"
            "font-weight:bold"
        )

    elif valor <= 5:

        return (
            "background-color:#ffd54f;"
            "color:black;"
            "font-weight:bold"
        )

    else:

        return (
            "background-color:#4caf50;"
            "color:white;"
            "font-weight:bold"
        )

# --------------------------------------------------
# TOTAL UNIDADES
# --------------------------------------------------

st.divider()

st.metric(
    "📦 Total unidades en inventario",
    int(df_filtrado["INVENTARIO"].sum())
)

# --------------------------------------------------
# TABLA INVENTARIO
# --------------------------------------------------

st.divider()

st.subheader("Inventario filtrado")

st.dataframe(
    df_filtrado.style.map(
        color_inventario,
        subset=["INVENTARIO"]
    ),
    use_container_width=True,
    hide_index=True
)