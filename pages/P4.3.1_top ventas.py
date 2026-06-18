import streamlit as st
import pandas as pd


VENTAS_PATH = "tablas/ventas_df.csv"
TODOS = "Todos"


st.set_page_config(
    page_title="Top ventas",
    page_icon="🏆",
    layout="wide",
)

st.title("🏆 Top ventas")


def limpiar_numero(valor):
    texto = str(valor).strip()

    if texto == "":
        return 0

    texto = (
        texto
        .replace("$", "")
        .replace(" ", "")
        .replace(",", "")
    )

    if "." in texto:
        texto = texto.split(".", 1)[0]

    return texto


@st.cache_data
def cargar_ventas():
    df = pd.read_csv(
        VENTAS_PATH,
        sep=";",
        dtype=str,
        keep_default_na=False,
    )

    df.columns = df.columns.str.strip()

    for columna in ["dia", "mes", "año", "cantidad"]:
        if columna in df.columns:
            df[columna] = (
                df[columna]
                .map(limpiar_numero)
            )
            df[columna] = pd.to_numeric(
                df[columna],
                errors="coerce",
            ).fillna(0).astype(int)

    columnas_texto = [
        "colegio",
        "articulo",
        "talla",
        "ID unico de artículo",
        "Estado Factura",
        "Producto pendiente por entregar",
    ]

    for columna in columnas_texto:
        if columna in df.columns:
            df[columna] = df[columna].astype(str).str.strip()

    return df


def opciones_con_todos(serie):
    valores = (
        serie
        .dropna()
        .astype(str)
        .str.strip()
    )
    valores = sorted(
        [valor for valor in valores.unique().tolist() if valor != ""]
    )
    return [TODOS] + valores


def opciones_numericas_con_todos(serie):
    valores = (
        pd.to_numeric(serie, errors="coerce")
        .dropna()
        .astype(int)
        .unique()
        .tolist()
    )
    return [TODOS] + sorted(valores)


def aplicar_filtro(df, columna, seleccion):
    if TODOS in seleccion or not seleccion:
        return df
    return df[df[columna].isin(seleccion)]


df_ventas = cargar_ventas()

st.header("Filtros")

col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)

with col1:
    filtro_anio = st.multiselect(
        "Año",
        opciones_numericas_con_todos(df_ventas["año"]),
        default=[TODOS],
        key="top_ventas_anio",
    )

df_filtrado = aplicar_filtro(df_ventas, "año", filtro_anio)

with col2:
    filtro_mes = st.multiselect(
        "Mes",
        opciones_numericas_con_todos(df_filtrado["mes"]),
        default=[TODOS],
        key="top_ventas_mes",
    )

df_filtrado = aplicar_filtro(df_filtrado, "mes", filtro_mes)

with col3:
    filtro_dia = st.multiselect(
        "Día",
        opciones_numericas_con_todos(df_filtrado["dia"]),
        default=[TODOS],
        key="top_ventas_dia",
    )

df_filtrado = aplicar_filtro(df_filtrado, "dia", filtro_dia)

with col4:
    filtro_colegio = st.multiselect(
        "Colegio",
        opciones_con_todos(df_filtrado["colegio"]),
        default=[TODOS],
        key="top_ventas_colegio",
    )

df_filtrado = aplicar_filtro(df_filtrado, "colegio", filtro_colegio)

with col5:
    filtro_articulo = st.multiselect(
        "Artículo",
        opciones_con_todos(df_filtrado["articulo"]),
        default=[TODOS],
        key="top_ventas_articulo",
    )

df_filtrado = aplicar_filtro(df_filtrado, "articulo", filtro_articulo)

with col6:
    filtro_talla = st.multiselect(
        "Talla",
        opciones_con_todos(df_filtrado["talla"]),
        default=[TODOS],
        key="top_ventas_talla",
    )

df_filtrado = aplicar_filtro(df_filtrado, "talla", filtro_talla)

st.divider()

if df_filtrado.empty:
    st.warning("No hay ventas para los filtros seleccionados.")
    st.stop()

total_unidades = int(df_filtrado["cantidad"].sum())
total_facturas = df_filtrado["ID unico de factura"].nunique()
total_productos = df_filtrado["ID unico de artículo"].nunique()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Unidades vendidas", f"{total_unidades:,}")

with col2:
    st.metric("Facturas", f"{total_facturas:,}")

with col3:
    st.metric("Productos únicos", f"{total_productos:,}")

st.divider()

df_filtrado = df_filtrado.copy()
df_filtrado["producto"] = (
    df_filtrado["colegio"].astype(str)
    + " | "
    + df_filtrado["articulo"].astype(str)
    + " | "
    + df_filtrado["talla"].astype(str)
)

top_producto = (
    df_filtrado
    .groupby(
        ["colegio", "articulo", "talla", "producto"],
        as_index=False,
    )
    .agg(
        unidades=("cantidad", "sum"),
    )
    .sort_values(
        "unidades",
        ascending=False,
    )
)

top_colegio = (
    df_filtrado
    .groupby("colegio", as_index=False)
    .agg(
        unidades=("cantidad", "sum"),
    )
    .sort_values(
        "unidades",
        ascending=False,
    )
)

top_articulo = (
    df_filtrado
    .groupby("articulo", as_index=False)
    .agg(
        unidades=("cantidad", "sum"),
    )
    .sort_values(
        "unidades",
        ascending=False,
    )
)

top_talla = (
    df_filtrado
    .groupby("talla", as_index=False)
    .agg(
        unidades=("cantidad", "sum"),
    )
    .sort_values(
        "unidades",
        ascending=False,
    )
)

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Producto",
        "Colegio",
        "Artículo",
        "Talla",
    ]
)

with tab1:
    st.subheader("Top productos por unidades")

    chart_data = (
        top_producto
        .head(15)
        .sort_values("unidades", ascending=True)
        .set_index("producto")["unidades"]
    )

    st.bar_chart(chart_data)

    st.dataframe(
        top_producto,
        use_container_width=True,
        hide_index=True,
    )

with tab2:
    st.subheader("Top colegios")
    st.bar_chart(
        top_colegio
        .head(15)
        .sort_values("unidades", ascending=True)
        .set_index("colegio")["unidades"]
    )
    st.dataframe(
        top_colegio,
        use_container_width=True,
        hide_index=True,
    )

with tab3:
    st.subheader("Top artículos")
    st.bar_chart(
        top_articulo
        .head(15)
        .sort_values("unidades", ascending=True)
        .set_index("articulo")["unidades"]
    )
    st.dataframe(
        top_articulo,
        use_container_width=True,
        hide_index=True,
    )

with tab4:
    st.subheader("Top tallas")
    st.bar_chart(
        top_talla
        .head(15)
        .sort_values("unidades", ascending=True)
        .set_index("talla")["unidades"]
    )
    st.dataframe(
        top_talla,
        use_container_width=True,
        hide_index=True,
    )
