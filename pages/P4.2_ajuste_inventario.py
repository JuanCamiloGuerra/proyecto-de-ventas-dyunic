import streamlit as st
import pandas as pd

# --------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------

st.set_page_config(
    page_title="AJUSTE DE INVENTARIO",
    page_icon="🔄",
    layout="wide"
)

st.title("🔄 AJUSTE DE INVENTARIO")

# --------------------------------------------------
# CARGAR TABLAS
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

df_motivos = pd.read_csv(
    "tablas/ajustes de inventario.csv",
    sep=";",
    header=None,
    keep_default_na=False
)

# --------------------------------------------------
# CREAR CARRITO
# --------------------------------------------------

if "carrito_ajustes" not in st.session_state:

    st.session_state.carrito_ajustes = pd.DataFrame(
        columns=[
            "Eliminar",
            "Movimiento",
            "Motivo",
            "Colegio",
            "Articulo",
            "Talla",
            "Cantidad",
            "Costo Unitario",
            "Subtotal",
            "ID_BUSQUEDA"
        ]
    )

# --------------------------------------------------
# SELECCIÓN DE PRODUCTO
# --------------------------------------------------

st.header("Registro de movimiento")

col1, col2, col3 = st.columns(3)

with col1:

    movimiento = st.selectbox(
        "Movimiento",
        [
            "INGRESA",
            "SALE"
        ]
    )

with col2:

    motivo = st.selectbox(
        "Motivo",
        df_motivos.iloc[:, 0]
        .dropna()
        .tolist()
    )

with col3:

    cantidad = st.number_input(
        "Cantidad",
        min_value=1,
        value=1,
        step=1
    )

st.divider()

col1, col2, col3 = st.columns(3)

with col1:

    colegio = st.selectbox(
        "Colegio",
        df_colegios.iloc[:, 0]
        .dropna()
        .tolist()
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
        df_articulos.iloc[:, 0]
        .tolist()
    )

with col3:

    talla = st.selectbox(
        "Talla",
        df_tallas.iloc[:, 0]
        .dropna()
        .tolist()
    )

# --------------------------------------------------
# ID BÚSQUEDA
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
# SUBTOTAL
# --------------------------------------------------

subtotal = precio * cantidad

# --------------------------------------------------
# INFORMACIÓN ENCONTRADA
# --------------------------------------------------

st.subheader("Información encontrada")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.text_input(
        "ID BUSQUEDA",
        value=id_busqueda,
        disabled=True
    )

with col2:

    st.metric(
        "Costo Unitario",
        f"${precio:,.0f}"
    )

with col3:

    st.metric(
        "Inventario Actual",
        inventario
    )

with col4:

    st.metric(
        "Valor Movimiento",
        f"${subtotal:,.0f}"
    )

# --------------------------------------------------
# AÑADIR AL CARRITO
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
            "Movimiento": movimiento,
            "Motivo": motivo,
            "Colegio": colegio,
            "Articulo": articulo,
            "Talla": talla,
            "Cantidad": cantidad,
            "Costo Unitario": precio,
            "Subtotal": subtotal,
            "ID_BUSQUEDA": id_busqueda
        }]
    )

    st.session_state.carrito_ajustes = pd.concat(
        [
            st.session_state.carrito_ajustes,
            nueva_fila
        ],
        ignore_index=True
    )

    st.success(
        "Movimiento agregado al carrito"
    )

# --------------------------------------------------
# CARRITO
# --------------------------------------------------

st.divider()

st.header("Carrito de ajustes")

st.session_state.carrito_ajustes = st.data_editor(
    st.session_state.carrito_ajustes,
    use_container_width=True,
    hide_index=True,

    disabled=[
        "Movimiento",
        "Motivo",
        "Colegio",
        "Articulo",
        "Talla",
        "Cantidad",
        "Costo Unitario",
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
# ELIMINAR
# --------------------------------------------------

col1, col2, col3 = st.columns([1, 2, 1])

with col2:

    eliminar = st.button(
        "🗑️ Eliminar seleccionados",
        use_container_width=True
    )

if eliminar:

    st.session_state.carrito_ajustes = (
        st.session_state.carrito_ajustes[
            st.session_state.carrito_ajustes["Eliminar"] == False
        ]
        .reset_index(drop=True)
    )

    st.rerun()

# --------------------------------------------------
# RESUMEN
# --------------------------------------------------

total_unidades = (
    st.session_state.carrito_ajustes["Cantidad"]
    .sum()
)

valor_ingresa = (
    st.session_state.carrito_ajustes[
        st.session_state.carrito_ajustes["Movimiento"]
        == "INGRESA"
    ]["Subtotal"]
    .sum()
)

valor_sale = (
    st.session_state.carrito_ajustes[
        st.session_state.carrito_ajustes["Movimiento"]
        == "SALE"
    ]["Subtotal"]
    .sum()
)

diferencia = valor_sale - valor_ingresa

st.divider()

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "📦 Total unidades",
        total_unidades
    )

with col2:

    st.metric(
        "📥 Valor ingresa",
        f"${valor_ingresa:,.0f}"
    )

with col3:

    st.metric(
        "📤 Valor sale",
        f"${valor_sale:,.0f}"
    )

with col4:

    st.metric(
        "💰 Diferencia",
        f"${abs(diferencia):,.0f}"
    )

if diferencia > 0:

    st.warning(
        f"Cliente debe pagar ${diferencia:,.0f}"
    )

elif diferencia < 0:

    st.info(
        f"Debe devolverse ${abs(diferencia):,.0f}"
    )

else:

    st.success(
        "Cambio sin diferencia económica"
    )

# --------------------------------------------------
# REGISTRAR AJUSTE
# --------------------------------------------------

st.divider()

registrar = st.button(
    "✅ Registrar ajuste",
    use_container_width=True
)

if registrar:

    # ------------------------------------------
    # VALIDAR CARRITO
    # ------------------------------------------

    if len(st.session_state.carrito_ajustes) == 0:

        st.error(
            "No hay movimientos para registrar."
        )

        st.stop()

    # ------------------------------------------
    # FECHA Y HORA BOGOTÁ
    # ------------------------------------------

    from datetime import datetime
    from zoneinfo import ZoneInfo

    ahora = datetime.now(
        ZoneInfo("America/Bogota")
    )

    fecha = ahora.strftime(
        "%d/%m/%Y"
    )

    # ------------------------------------------
    # CARGAR INVENTARIO
    # ------------------------------------------

    df_inventario = pd.read_csv(
        "tablas/inventario.csv",
        sep=";"
    )

    # ------------------------------------------
    # VALIDAR EXISTENCIA
    # ------------------------------------------

    for _, fila in (
        st.session_state.carrito_ajustes.iterrows()
    ):

        id_producto = str(
            fila["ID_BUSQUEDA"]
        )

        existe = (
            df_inventario["ID_BUSQUEDA"]
            .astype(str)
            .eq(id_producto)
            .any()
        )

        if not existe:

            st.error(
                f"""
                Producto no encontrado
                en inventario:

                {id_producto}

                Elimine el producto
                del carrito o créelo
                primero en inventario.
                """
            )

            st.stop()

    # ------------------------------------------
    # AJUSTAR INVENTARIO
    # ------------------------------------------

    for _, fila in (
        st.session_state.carrito_ajustes.iterrows()
    ):

        id_producto = str(
            fila["ID_BUSQUEDA"]
        )

        cantidad = int(
            fila["Cantidad"]
        )

        movimiento = str(
            fila["Movimiento"]
        )

        indice = df_inventario[
            df_inventario["ID_BUSQUEDA"]
            .astype(str)
            .eq(id_producto)
        ].index[0]

        inventario_actual = int(
            df_inventario.loc[
                indice,
                "INVENTARIO"
            ]
        )

        if movimiento == "INGRESA":

            nuevo_inventario = (
                inventario_actual
                + cantidad
            )

        else:

            nuevo_inventario = (
                inventario_actual
                - cantidad
            )

        df_inventario.loc[
            indice,
            "INVENTARIO"
        ] = nuevo_inventario

    # ------------------------------------------
    # GUARDAR INVENTARIO
    # ------------------------------------------

    df_inventario.to_csv(
        "tablas/inventario.csv",
        sep=";",
        index=False
    )

    # ------------------------------------------
    # CARGAR REGISTRO AJUSTES
    # ------------------------------------------

    df_registro = pd.read_csv(
        "tablas/ajustes_inventario_registro.csv",
        sep=";"
        
    )

    # ------------------------------------------
    # CREAR REGISTROS
    # ------------------------------------------

    

    # ------------------------------------------
    # CREAR REGISTROS
    # ------------------------------------------

    registros_nuevos = []

    for _, fila in (
        st.session_state.carrito_ajustes.iterrows()
    ):

        registros_nuevos.append({

            "Fecha": fecha,

            "Día": ahora.day,

            "Mes": ahora.month,

            "Año": ahora.year,

            "Accion": fila["Movimiento"],

            "Desc.1": fila["Colegio"],

            "Desc.2": fila["Articulo"],

            "Talla": fila["Talla"],

            "cantidad": fila["Cantidad"],

            "Motivo": fila["Motivo"],

            "INVENTARIO": "",

            "Val. Unitario": fila["Costo Unitario"],

            "Subtotal": fila["Subtotal"]

        })

    registros_nuevos = pd.DataFrame(
        registros_nuevos
    )
    st.write(registros_nuevos)
    # ------------------------------------------
    # AGREGAR REGISTROS
    # ------------------------------------------

    df_registro = pd.concat(
        [
            df_registro,
            registros_nuevos
        ],
        ignore_index=True
    )

    # ------------------------------------------
    # GUARDAR REGISTRO
    # ------------------------------------------

    df_registro.to_csv(
        "tablas/ajustes_inventario_registro.csv",
        sep=";",
        index=False
    )

    # ------------------------------------------
    # LIMPIAR CARRITO
    # ------------------------------------------

    st.session_state.carrito_ajustes = pd.DataFrame(
        columns=[
            "Eliminar",
            "Movimiento",
            "Motivo",
            "Colegio",
            "Articulo",
            "Talla",
            "Cantidad",
            "Costo Unitario",
            "Subtotal",
            "ID_BUSQUEDA"
        ]
    )

    st.success(
        "Ajuste registrado correctamente."
    )

    st.rerun()

# ---------------------------------------
# PRUEBA REGISTRO AJUSTES INVENTARIO
# ---------------------------------------

st.divider()

st.subheader(
    "🔄 Últimos registros de ajustes de inventario"
)

df_ajustes_tmp = pd.read_csv(
    "tablas/ajustes_inventario_registro.csv",
    sep=";"
)

st.dataframe(
    df_ajustes_tmp.tail(5),
    use_container_width=True
)