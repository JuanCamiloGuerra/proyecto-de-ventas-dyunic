import streamlit as st
import pandas as pd
from datetime import datetime

# --------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------

st.set_page_config(
    page_title="VENTAS DYUNIC",
    page_icon="🛒",
    layout="wide"
)

st.title("VENTAS DYUNIC")

# --------------------------------------------------
# CARGA DEL ARCHIVO
# --------------------------------------------------

if "df" not in st.session_state:

    df = pd.read_csv(
        "ventas_df.csv",
        sep=";",
        header=None,
        encoding="utf-8"
    )

    # Encabezados en la fila 2
    df.columns = df.iloc[2]

    # Eliminar filas basura
    df = df.iloc[3:].reset_index(drop=True)

    st.session_state.df = df
    
# --------------------------------------------------
# LISTAS EDITABLES
# --------------------------------------------------

COLEGIOS = [
    "liceo pupo jimenez",
    "colegio 2",
    "colegio 3"
]

ARTICULOS = [
    "falda",
    "bombacho",
    "camiseta fisica",
    "camiseta diario",
    "pantalon"
]

TALLAS = [
    "4",
    "6",
    "8",
    "10",
    "12",
    "14",
    "16",
    "XS",
    "S",
    "M",
    "L",
    "XL"
]

# --------------------------------------------------
# FORMULARIO
# --------------------------------------------------

st.header("Registrar Venta")

with st.form("formulario_venta"):

    nombre = st.text_input(
        "Nombre del cliente"
    )

    colegio = st.selectbox(
        "Colegio",
        COLEGIOS
    )

    articulo = st.selectbox(
        "Artículo",
        ARTICULOS
    )

    talla = st.selectbox(
        "Talla",
        TALLAS
    )

    cantidad = st.number_input(
        "Cantidad",
        min_value=1,
        value=1,
        step=1
    )

    guardar = st.form_submit_button(
        "Guardar Venta"
    )



# --------------------------------------------------
# GUARDAR REGISTRO
# --------------------------------------------------

if guardar:

    fecha_hoy = datetime.now()

    nuevo_registro = {

        "ID unico de factura": "",

        "fecha": fecha_hoy.strftime("%d/%m/%Y"),

        "dia": fecha_hoy.day,

        "mes": fecha_hoy.month,

        "año": fecha_hoy.year,

        "colegio": colegio,

        "articulo": articulo,

        "talla": talla,

        "hombro": "",

        "talle": "",

        "cintura": "",

        "largo": "",

        "ID unico de artículo":
            f"{colegio}_{articulo}_{talla}",

        "cantidad": cantidad,

        "precio individual": "",

        "subtotal": "",

        "Estado Factura": "",

        "Producto pendiente por entregar": "",

        "Clasificación_antiguo": "",

        "Método de pago_antiguo": "",

        "Nombre": nombre
    }

    df_nuevo = pd.DataFrame([nuevo_registro])

    # Agregar al final del dataframe
    st.session_state.df = pd.concat(
        [st.session_state.df, df_nuevo],
        ignore_index=True
    )

    st.success("Venta registrada correctamente")

# --------------------------------------------------
# ÚLTIMAS VENTAS
# --------------------------------------------------

st.header("Últimas 10 ventas registradas")

ultimas_10 = (
    st.session_state.df
    .tail(10)      # toma las últimas 10 filas
    .iloc[::-1]    # las muestra de más reciente a más antigua
)

st.dataframe(
    ultimas_10,
    use_container_width=True,
    hide_index=True
)