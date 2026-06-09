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

st.title("VENTAS DYUNIC 1")

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

if "carrito_1" not in st.session_state:

    st.session_state.carrito_1 = pd.DataFrame(
        columns=[
            "Eliminar",
            "Colegio",
            "Articulo",
            "Talla",
            "Cantidad",
            "Valor Unitario",
            "Subtotal",
            "ID_BUSQUEDA"
        ]
    )


# --------------------------------------------------
# DATOS DEL CLIENTE
# --------------------------------------------------

st.header("Datos del cliente")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:

    nombre_cliente = st.text_input(
        "Nombre"
    )

with col2:

    telefono_cliente = st.text_input(
        "Teléfono"
    )

with col3:

    documento_cliente = st.text_input(
        "Documento"
    )

with col4:

    id_membrete = st.text_input(
        "ID Membrete"
    )

with col5:

    sede = st.selectbox(
        "Sede",
        [
            "C-BGT",
            "C-BCL",
            "C-BBV",
            "J-BCL",
            "J-BBV",
            "K-BCL"
        ]
    )

# --------------------------------------------------
# ID FACTURA AUTOMÁTICO
# --------------------------------------------------

fecha_factura = datetime.now().strftime("%Y%m%d")

id_factura = (
    f"{fecha_factura}-"
    f"{documento_cliente}-"
    f"{telefono_cliente}-"
    f"{id_membrete}-"
    f"{sede}"
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
            "Subtotal": subtotal,
            "ID_BUSQUEDA": id_busqueda
        }]
    )

    st.session_state.carrito_1 = pd.concat(
        [st.session_state.carrito_1, nueva_fila],
        ignore_index=True
    )

    st.success("Producto añadido al carrito")

st.divider()

# --------------------------------------------------
# MOSTRAR CARRITO
# --------------------------------------------------

st.header("Carrito")

st.session_state.carrito_1 = st.data_editor(
    st.session_state.carrito_1,
    use_container_width=True,
    hide_index=True,

    disabled=[
        "Colegio",
        "Articulo",
        "Talla",
        "Cantidad",
        "Valor Unitario",
        "Subtotal",
        "ID_BUSQUEDA"
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

    st.session_state.carrito_1 = (
        st.session_state.carrito_1[
            st.session_state.carrito_1["Eliminar"] == False
        ]
        .reset_index(drop=True)
    )

    st.rerun()

# --------------------------------------------------
# TOTAL DEL CARRITO
# --------------------------------------------------

total_carrito_1 = (
    st.session_state.carrito_1["Subtotal"]
    .sum()
)

col1, col2 = st.columns([2, 1])

with col1:

    st.subheader("💰 TOTAL CARRITO")

with col2:

    st.markdown(
        f"<h2 style='text-align:right;'>${total_carrito_1:,.0f}</h2>",
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
    total_carrito_1
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




# --------------------------------------------------
# BOTÓN CERRAR VENTA
# --------------------------------------------------

st.divider()

cerrar_venta = st.button(
    "✅ Cerrar venta",
    use_container_width=True
)

# --------------------------------------------------
# CERRAR VENTA
# --------------------------------------------------

if cerrar_venta:

    # ------------------------------------------
    # VALIDACIONES
    # ------------------------------------------

    if len(st.session_state.carrito_1) == 0:

        st.error(
            "El carrito está vacío."
        )
        st.stop()

    if nombre_cliente.strip() == "":

        st.error(
            "Debe ingresar el nombre del cliente."
        )
        st.stop()

    if telefono_cliente.strip() == "":

        st.error(
            "Debe ingresar el teléfono."
        )
        st.stop()

    if documento_cliente.strip() == "":

        st.error(
            "Debe ingresar el documento."
        )
        st.stop()

    # ------------------------------------------
    # ESTADO FACTURA
    # ------------------------------------------

    if valor_pendiente == 0:

        estado_factura = "PAGADA"

    else:

        estado_factura = "PENDIENTE"

    # ------------------------------------------
    # FECHA BONITA
    # ------------------------------------------

    dias_semana = [
        "lunes",
        "martes",
        "miércoles",
        "jueves",
        "viernes",
        "sábado",
        "domingo"
    ]

    meses_texto = [
        "",
        "enero",
        "febrero",
        "marzo",
        "abril",
        "mayo",
        "junio",
        "julio",
        "agosto",
        "septiembre",
        "octubre",
        "noviembre",
        "diciembre"
    ]

    ahora = datetime.now()

    fecha_larga = (
        f"{dias_semana[ahora.weekday()]}, "
        f"{ahora.day} de "
        f"{meses_texto[ahora.month]} de "
        f"{ahora.year}"
    )

    # ------------------------------------------
    # CREAR REGISTROS PARA ventas_df
    # ------------------------------------------
    

    if st.session_state.carrito_1.empty:

     st.error(
        "No existen productos para registrar."
    )

    st.stop()

    ventas_nuevas = pd.DataFrame()

    ventas_nuevas["colegio"] = (
        st.session_state.carrito_1["Colegio"]
    )

    ventas_nuevas["articulo"] = (
        st.session_state.carrito_1["Articulo"]
    )

    ventas_nuevas["talla"] = (
        st.session_state.carrito_1["Talla"]
    )

    ventas_nuevas["cantidad"] = (
        st.session_state.carrito_1["Cantidad"]
    )

    ventas_nuevas["precio individual"] = (
        st.session_state.carrito_1["Valor Unitario"]
    )

    ventas_nuevas["subtotal"] = (
        st.session_state.carrito_1["Subtotal"]
    )

    ventas_nuevas["Estado Factura"] = (
        estado_factura
    )

    ventas_nuevas["ID unico de factura"] = (
        id_factura
    )

    ventas_nuevas["fecha"] = (
        fecha_larga
    )

    ventas_nuevas["día"] = (
        ahora.day
    )

    ventas_nuevas["mes"] = (
        ahora.month
    )

    ventas_nuevas["año"] = (
        ahora.year
    )

    ventas_nuevas["ID unico de artículo"] = (
        st.session_state.carrito_1["ID_BUSQUEDA"]
    )

    # ------------------------------------------
    # CARGAR ventas_df
    # ------------------------------------------

    df_ventas = pd.read_csv(
        "tablas/ventas_df.csv",
        sep=";"
    )

    # ------------------------------------------
    # EVITAR FACTURAS DUPLICADAS
    # ------------------------------------------

    if (
        df_ventas["ID unico de factura"]
        .astype(str)
        .eq(id_factura)
        .any()
    ):

        st.error(
            "Esta factura ya fue registrada."
        )

        st.stop()

    # ------------------------------------------
    # AGREGAR REGISTROS
    # ------------------------------------------

    df_ventas = pd.concat(
        [
            df_ventas,
            ventas_nuevas
        ],
        ignore_index=True
    )

    # ------------------------------------------
    # GUARDAR CSV
    # ------------------------------------------

    df_ventas.to_csv(
        "tablas/ventas_df.csv",
        sep=";",
        index=False
    )

    # ------------------------------------------
    # LIMPIAR CARRITO
    # ------------------------------------------

    st.session_state.carrito_1 = pd.DataFrame(
        columns=[
            "Eliminar",
            "Colegio",
            "Articulo",
            "Talla",
            "Cantidad",
            "Valor Unitario",
            "Subtotal",
            "ID_BUSQUEDA"
        ]
    )

    # ------------------------------------------
    # MENSAJE FINAL
    # ------------------------------------------

    st.success(
        "Venta registrada correctamente."
    )

    st.rerun()