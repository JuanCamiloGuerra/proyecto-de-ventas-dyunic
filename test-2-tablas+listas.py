# Paquetes para usar tablas y listas
import streamlit as st
import pandas as pd
from datetime import datetime

# --------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------            
st.set_page_config(
    page_title="VENTAS DYUNIC-PRUEBA TABLAS + LISTAS",
    page_icon="🛒",
    layout="wide"
)
st.title("VENTAS DYUNIC")

# --------------------------------------------------
# --------------------------------------------------
# CARGAR TABLAS AUXILIARES
# --------------------------------------------------

df_colegios = pd.read_csv("tablas/colegios.csv", sep=";")
df_tallas = pd.read_csv("tablas/tallas.csv", sep=";")
df_precios = pd.read_csv("tablas/precios.csv", sep=";")
df_inventario = pd.read_csv("tablas/inventario.csv", sep=";")

# --------------------------------------------------
# FORMULARIO DE PRUEBA
# --------------------------------------------------

st.header("Prueba de selección de producto")

# COLEGIO
colegio = st.selectbox(
    "Colegio",
    df_colegios.iloc[:, 0].dropna().tolist()
)

# --------------------------------------------------
# CARGAR ARCHIVO DEL COLEGIO SELECCIONADO
# --------------------------------------------------

archivo_colegio = f"tablas/{colegio}.csv"

df_articulos = pd.read_csv(
    archivo_colegio,
    sep=";"
)

# ARTICULO
articulo = st.selectbox(
    "Artículo",
    df_articulos.iloc[:, 0].dropna().tolist()
)

# TALLA
talla = st.selectbox(
    "Talla",
    df_tallas.iloc[:, 0].dropna().tolist()
)

# CANTIDAD
cantidad = st.number_input(
    "Cantidad",
    min_value=1,
    value=1,
    step=1
)

# --------------------------------------------------
# CREAR ID DE BUSQUEDA
# --------------------------------------------------

id_busqueda = f"{colegio}_{articulo}_{talla}"

# --------------------------------------------------
# BUSCAR PRECIO
# --------------------------------------------------

precio_df = df_precios[
    df_precios["ID_BUSQUEDA"] == id_busqueda
]

if len(precio_df) > 0:

    precio = precio_df.iloc[0]["VALOR AÑO PRESENTE"]

else:

    precio = 0

# --------------------------------------------------
# BUSCAR INVENTARIO
# --------------------------------------------------

inventario_df = df_inventario[
    df_inventario["ID_BUSQUEDA"] == id_busqueda
]

if len(inventario_df) > 0:

    inventario = inventario_df.iloc[0]["INVENTARIO"]

else:

    inventario = 0

# --------------------------------------------------
# CALCULAR SUBTOTAL
# --------------------------------------------------

subtotal = precio * cantidad

# --------------------------------------------------
# MOSTRAR RESULTADOS
# --------------------------------------------------

st.subheader("Información encontrada")

col1, col2 = st.columns(2)

with col1:

    st.write("ID BUSQUEDA")
    st.info(id_busqueda)

    st.write("Precio")
    st.success(f"${precio:,.0f}")

with col2:

    st.write("Inventario")
    st.warning(inventario)

    st.write("Subtotal")
    st.success(f"${subtotal:,.0f}")