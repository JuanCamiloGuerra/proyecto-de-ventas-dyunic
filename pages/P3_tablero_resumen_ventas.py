import streamlit as st
import pandas as pd

# --------------------------------------------------
# CARGAR FACTURACIÓN
# --------------------------------------------------

df_facturacion = pd.read_csv(
    "tablas/facturacion_ventas.csv",
    sep=";"
)
# --------------------------------------------------
# ELIMINAR FILAS VACÍAS
# --------------------------------------------------

df_facturacion = df_facturacion[
    df_facturacion["ID unico de factura"]
    .notna()
]

df_facturacion = df_facturacion[
    df_facturacion["ID unico de factura"]
    .astype(str)
    .str.strip()
    != ""
]

df_facturacion = df_facturacion.reset_index(
    drop=True
)
# --------------------------------------------------
# LIMPIAR COLUMNAS
# --------------------------------------------------

df_facturacion.columns = (
    df_facturacion.columns
    .str.strip()
)

# --------------------------------------------------
# CONVERTIR COLUMNAS NUMÉRICAS
# --------------------------------------------------

columnas_monetarias = [
    "total efectivo",
    "total tarjeta",
    "total transfencia",
    "total pendiente"
]

for col in columnas_monetarias:

    df_facturacion[col] = (
        df_facturacion[col]
        .astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )

    df_facturacion[col] = pd.to_numeric(
        df_facturacion[col],
        errors="coerce"
    )

for col in ["Año", "Mes", "Día"]:

    df_facturacion[col] = pd.to_numeric(
        df_facturacion[col],
        errors="coerce"
    )

# --------------------------------------------------
# CONVERTIR A ENTEROS
# --------------------------------------------------

df_facturacion["Año"] = (
    df_facturacion["Año"]
    .fillna(0)
    .astype(int)
)

df_facturacion["Mes"] = (
    df_facturacion["Mes"]
    .fillna(0)
    .astype(int)
)

df_facturacion["Día"] = (
    df_facturacion["Día"]
    .fillna(0)
    .astype(int)
)
    
    

# --------------------------------------------------
# FILTROS
# --------------------------------------------------

st.header("Filtros")

col1, col2, col3 = st.columns(3)

# AÑO

with col1:

    lista_años = sorted(
        df_facturacion["Año"]
        .dropna()
        .unique()
        .tolist()
    )

    año = st.selectbox(
        "Año",
        lista_años
    )

# MESES

with col2:

    lista_meses = sorted(
    df_facturacion[
        df_facturacion["Año"] == año
    ]["Mes"]
    .dropna()
    .astype(int)
    .unique()
    .tolist()
)

    meses = st.multiselect(
        "Mes",
        lista_meses,
        default=lista_meses
    )

# DÍAS

with col3:

    lista_dias = sorted(
    df_facturacion[
        (df_facturacion["Año"] == año)
        &
        (df_facturacion["Mes"].isin(meses))
    ]["Día"]
    .dropna()
    .astype(int)
    .unique()
    .tolist()
)

    dias = st.multiselect(
        "Día",
        lista_dias,
        default=lista_dias
    )

# --------------------------------------------------
# FILTRAR
# --------------------------------------------------

df_filtrado = df_facturacion[
    (df_facturacion["Año"] == año)
    &
    (df_facturacion["Mes"].isin(meses))
    &
    (df_facturacion["Día"].isin(dias))
].copy()

# --------------------------------------------------
# TOTAL VENDIDO
# --------------------------------------------------

total_vendido = (
    df_filtrado["total efectivo"].sum()
    +
    df_filtrado["total tarjeta"].sum()
    +
    df_filtrado["total transfencia"].sum()
)

total_pendiente = (
    df_filtrado["total pendiente"]
    .sum()
)

# --------------------------------------------------
# MÉTRICAS
# --------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "💰 TOTAL VENDIDO",
        f"${total_vendido:,.0f}"
    )

with col2:

    st.metric(
        "⚠️ TOTAL PENDIENTE",
        f"${total_pendiente:,.0f}"
    )
# --------------------------------------------------
# TABLA RESUMEN
# --------------------------------------------------

df_resumen = (
    df_filtrado
    .groupby(
        ["Año", "Mes", "Día"],
        as_index=False
    )
    .agg({
        "total efectivo": "sum",
        "total tarjeta": "sum",
        "total transfencia": "sum",
        "total pendiente": "sum"
    })
)

df_resumen["Total Ventas"] = (
    df_resumen["total efectivo"]
    +
    df_resumen["total tarjeta"]
    +
    df_resumen["total transfencia"]
)
# --------------------------------------------------
# ORDENAR
# --------------------------------------------------

df_resumen = df_resumen.sort_values(
    ["Año", "Mes", "Día"]
)

# --------------------------------------------------
# MOSTRAR TABLA
# --------------------------------------------------

st.divider()

st.subheader("Resumen de ventas")

st.dataframe(
    df_resumen,
    use_container_width=True,
    hide_index=True
)

# --------------------------------------------------
# PRODUCTOS PENDIENTES POR ENTREGAR
# --------------------------------------------------

st.divider()

st.header("📦 Productos pendientes por entregar")

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

df_ventas.columns = (
    df_ventas.columns
    .str.strip()
)

# --------------------------------------------------
# FILTRAR SOLO PENDIENTES
# --------------------------------------------------

df_pendientes = df_ventas[
    df_ventas["Producto pendiente por entregar"]
    .astype(str)
    .str.upper()
    .str.strip()
    == "SI"
].copy()

# --------------------------------------------------
# COLUMNAS DE VENTAS
# --------------------------------------------------

df_pendientes = df_pendientes[
    [
        "ID unico de factura",
        "fecha",
        "ID unico de artículo",
        "cantidad",
        "Estado Factura"
    ]
]

# --------------------------------------------------
# COLUMNAS DE FACTURACIÓN
# --------------------------------------------------

df_clientes = df_facturacion[
    [
        "ID unico de factura",
        "Nombre cliente",
        "Numero de contacto",
        "total pendiente"
    ]
].copy()

# --------------------------------------------------
# RENOMBRAR COLUMNAS
# --------------------------------------------------

df_clientes = df_clientes.rename(
    columns={
        "Nombre cliente": "Nombre",
        "Numero de contacto": "Celular",
        "total pendiente": "Saldo pendiente"
    }
)

# --------------------------------------------------
# UNIR TABLAS
# --------------------------------------------------

df_pendientes = df_pendientes.merge(
    df_clientes,
    on="ID unico de factura",
    how="left"
)

# --------------------------------------------------
# MOSTRAR TABLA
# --------------------------------------------------

st.dataframe(
    df_pendientes,
    use_container_width=True,
    hide_index=True
)