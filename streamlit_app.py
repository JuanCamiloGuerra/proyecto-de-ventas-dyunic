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
# CARGAR TABLAS AUXILIARES
# --------------------------------------------------

df_colegios = pd.read_csv(
    "tablas/colegios.csv",
    sep=";",
    header=None,
    keep_default_na=False
)

df_tallas = pd.read_csv(
    "tablas/tallas.csv",
    sep=";",
    header=None,
    keep_default_na=False
)

df_precios = pd.read_csv(
    "tablas/precios.csv",
    sep=";"
)

df_inventario = pd.read_csv(
    "tablas/inventario.csv",
    sep=";"
)

# --------------------------------------------------
# CREAR CARRITO
# --------------------------------------------------

if "carrito" not in st.session_state:

    st.session_state.carrito = pd.DataFrame(
        columns=[
            "Eliminar",
            "Colegio",
            "Articulo",
            "Talla",
            "Cantidad",
            "Valor Unitario",
            "Subtotal"
        ]
    )


# --------------------------------------------------
# DATOS DEL CLIENTE
# --------------------------------------------------

st.header("Datos del cliente")

col1, col2, col3, col4 = st.columns(4)

with col1:
    nombre_cliente = st.text_input("Nombre")

with col2:
    telefono_cliente = st.text_input("Teléfono")

with col3:
    documento_cliente = st.text_input("Documento")

with col4:
    id_membrete = st.text_input("ID Membrete")

fecha_factura = datetime.now().strftime("%Y%m%d")

id_factura = (
    f"{fecha_factura}-"
    f"{documento_cliente}-"
    f"{telefono_cliente}-"
    f"{id_membrete}"
)

st.text_input(
    "ID Factura",
    value=id_factura,
    disabled=True
)

st.divider()


# --------------------------------------------------
# FORMULARIO DE PRODUCTO
# --------------------------------------------------

st.header("Selección de producto")

col1, col2, col3, col4 = st.columns(4)

with col1:

    colegio = st.selectbox(
        "Colegio",
        df_colegios.iloc[:, 0].dropna().tolist()
    )

with col2:

    archivo_colegio = f"tablas/{colegio}.csv"

    df_articulos = pd.read_csv(
        archivo_colegio,
        sep=";",
        header=None,
        keep_default_na=False
    )

    articulo = st.selectbox(
        "Artículo",
        df_articulos.iloc[:, 0].tolist()
    )

with col3:

    talla = st.selectbox(
        "Talla",
        df_tallas.iloc[:, 0].dropna().tolist()
    )

with col4:

    cantidad = st.number_input(
        "Cantidad",
        min_value=1,
        value=1,
        step=1
    )

# --------------------------------------------------
# CREAR ID DE BÚSQUEDA
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
# INFORMACIÓN ENCONTRADA
# --------------------------------------------------

st.subheader("Información encontrada")

col1, col2, col3, col4 = st.columns(4)

#with col1:

#    st.text_input(
#        "ID BUSQUEDA",
#        value=id_busqueda,
#        disabled=True
#    )
with col1:

    st.text_input(
        "ID BUSQUEDA",
        value=id_busqueda,
        disabled=True
    )


with col2:

    st.metric(
        "Precio",
        f"${precio:,.0f}"
    )

with col3:

    st.metric(
        "Inventario",
        inventario
    )

with col4:

    st.metric(
        "Subtotal",
        f"${subtotal:,.0f}"
    )

# --------------------------------------------------
# BOTÓN AÑADIR AL CARRITO
# --------------------------------------------------

col1, col2, col3 = st.columns([1, 2, 1])

with col2:

    añadir = st.button(
        "➕ Añadir al carrito",
        use_container_width=True
    )

if añadir:

    nueva_fila = pd.DataFrame(
        [{
            "Eliminar": False,
            "Colegio": colegio,
            "Articulo": articulo,
            "Talla": talla,
            "Cantidad": cantidad,
            "Valor Unitario": precio,
            "Subtotal": subtotal
        }]
    )

    st.session_state.carrito = pd.concat(
        [st.session_state.carrito, nueva_fila],
        ignore_index=True
    )

    st.success("Producto añadido al carrito")

st.divider()

# --------------------------------------------------
# MOSTRAR CARRITO
# --------------------------------------------------

st.header("Carrito")

st.session_state.carrito = st.data_editor(
    st.session_state.carrito,
    use_container_width=True,
    hide_index=True,

    disabled=[
        "Colegio",
        "Articulo",
        "Talla",
        "Cantidad",
        "Valor Unitario",
        "Subtotal"
    ],

    column_config={
        "Eliminar": st.column_config.CheckboxColumn(
            "Eliminar"
        )
    }
)

# --------------------------------------------------
# ELIMINAR PRODUCTOS SELECCIONADOS
# --------------------------------------------------

col1, col2, col3 = st.columns([1, 2, 1])

with col2:

    eliminar = st.button(
        "🗑️ Eliminar seleccionados",
        use_container_width=True
    )

if eliminar:

    st.session_state.carrito = (
        st.session_state.carrito[
            st.session_state.carrito["Eliminar"] == False
        ]
        .reset_index(drop=True)
    )

    st.rerun()

# --------------------------------------------------
# TOTAL DEL CARRITO
# --------------------------------------------------

total_carrito = (
    st.session_state.carrito["Subtotal"]
    .sum()
)

col1, col2 = st.columns([2, 1])

with col1:

    st.subheader("💰 TOTAL CARRITO")

with col2:

    st.markdown(
        f"<h2 style='text-align:right;'>${total_carrito:,.0f}</h2>",
        unsafe_allow_html=True
    )

# --------------------------------------------------
# MEDIOS DE PAGO
# --------------------------------------------------

st.divider()

st.subheader("💳 Medios de pago")

col1, col2, col3 = st.columns(3)

with col1:

    efectivo = st.number_input(
        "Efectivo",
        min_value=0,
        value=0,
        step=1000
    )

with col2:

    tarjeta = st.number_input(
        "Tarjeta",
        min_value=0,
        value=0,
        step=1000
    )

with col3:

    transferencia = st.number_input(
        "Transferencia",
        min_value=0,
        value=0,
        step=1000
    )

# --------------------------------------------------
# TOTAL REGISTRADO
# --------------------------------------------------

total_registrado = (
    efectivo
    + tarjeta
    + transferencia
)

# --------------------------------------------------
# VALOR PENDIENTE
# --------------------------------------------------

valor_pendiente = (
    total_carrito
    - total_registrado
)

st.divider()

# TOTAL REGISTRADO

col1, col2 = st.columns([2, 1])

with col1:

    st.subheader("💵 TOTAL REGISTRADO")

with col2:

    st.markdown(
        f"<h2 style='text-align:right;'>${total_registrado:,.0f}</h2>",
        unsafe_allow_html=True
    )

# VALOR PENDIENTE

col1, col2 = st.columns([2, 1])

with col1:

    st.subheader("⚠️ VALOR PENDIENTE")

with col2:

    st.markdown(
        f"<h2 style='text-align:right;'>${valor_pendiente:,.0f}</h2>",
        unsafe_allow_html=True
    )

if valor_pendiente == 0:

    st.success("Venta completamente pagada")

elif valor_pendiente > 0:

    st.warning(
        f"Cliente pendiente por pagar ${valor_pendiente:,.0f}"
    )

else:

    st.error(
        f"Se registraron ${abs(valor_pendiente):,.0f} de más"
    )