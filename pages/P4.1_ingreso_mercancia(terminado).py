import streamlit as st
import pandas as pd

# --------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------

st.set_page_config(
    page_title="INGRESO DE MERCANCÍA",
    page_icon="📦",
    layout="wide"
)

st.title("📦 INGRESO DE MERCANCÍA")

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

# --------------------------------------------------
# CREAR CARRITO
# --------------------------------------------------

if "carrito_ingreso" not in st.session_state:

    st.session_state.carrito_ingreso = pd.DataFrame(
        columns=[
            "Eliminar",
            "Colegio",
            "Articulo",
            "Talla",
            "Cantidad",
            "Costo Unitario",
            "Subtotal"
        ]
    )

# --------------------------------------------------
# SELECCIÓN DE PRODUCTO
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
        "Cantidad a ingresar",
        min_value=1,
        value=1,
        step=1
    )

# --------------------------------------------------
# ID BÚSQUEDA
# --------------------------------------------------

id_busqueda = f"{colegio}_{articulo}_{talla}"

# --------------------------------------------------
# PRECIO
# --------------------------------------------------

precio_df = df_precios[
    df_precios["ID_BUSQUEDA"] == id_busqueda
]

if len(precio_df) > 0:

    precio = precio_df.iloc[0]["VALOR AÑO PRESENTE"]

else:

    precio = 0

# --------------------------------------------------
# INVENTARIO
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
        "Valor Ingreso",
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
            "Colegio": colegio,
            "Articulo": articulo,
            "Talla": talla,
            "Cantidad": cantidad,
            "Costo Unitario": precio,
            "Subtotal": subtotal
        }]
    )

    st.session_state.carrito_ingreso = pd.concat(
        [
            st.session_state.carrito_ingreso,
            nueva_fila
        ],
        ignore_index=True
    )

    st.success("Producto añadido al carrito")

# --------------------------------------------------
# CARRITO
# --------------------------------------------------

st.divider()

st.header("Carrito de ingreso")

st.session_state.carrito_ingreso = st.data_editor(
    st.session_state.carrito_ingreso,
    use_container_width=True,
    hide_index=True,

    disabled=[
        "Colegio",
        "Articulo",
        "Talla",
        "Cantidad",
        "Costo Unitario",
        "Subtotal"
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

    st.session_state.carrito_ingreso = (
        st.session_state.carrito_ingreso[
            st.session_state.carrito_ingreso["Eliminar"] == False
        ]
        .reset_index(drop=True)
    )

    st.rerun()

# --------------------------------------------------
# TOTALES
# --------------------------------------------------

total_unidades = (
    st.session_state.carrito_ingreso["Cantidad"]
    .sum()
)

total_valor = (
    st.session_state.carrito_ingreso["Subtotal"]
    .sum()
)

st.divider()

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "📦 TOTAL UNIDADES",
        total_unidades
    )

with col2:

    st.metric(
        "💰 VALOR MERCANCÍA",
        f"${total_valor:,.0f}"
    )

# --------------------------------------------------
# REGISTRAR INGRESO
# --------------------------------------------------

st.divider()

registrar = st.button(
    "✅ Registrar ingreso de mercancía",
    use_container_width=True
)

if registrar:

    # ------------------------------------------
    # VALIDAR CARRITO
    # ------------------------------------------

    if len(st.session_state.carrito_ingreso) == 0:

        st.error(
            "El carrito está vacío."
        )

        st.stop()

    # ------------------------------------------
    # VALIDAR IDs DUPLICADOS EN INVENTARIO
    # ------------------------------------------

    ids_duplicados = (
        df_inventario["ID_BUSQUEDA"]
        .astype(str)
        .duplicated()
        .any()
    )

    if ids_duplicados:

        st.error(
            "Existen ID_BUSQUEDA duplicados en inventario.csv. "
            "Corrija el inventario antes de continuar."
        )

        st.stop()

    # ------------------------------------------
    # VALIDAR EXISTENCIA DE PRODUCTOS
    # ------------------------------------------

    for _, fila in st.session_state.carrito_ingreso.iterrows():

        id_producto = (
            f"{fila['Colegio']}_"
            f"{fila['Articulo']}_"
            f"{fila['Talla']}"
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
                El producto:

                {id_producto}

                no existe en inventario.

                Debe crearlo primero o
                eliminarlo del carrito.
                """
            )

            st.stop()

    # ------------------------------------------
    # SUMAR INVENTARIO
    # ------------------------------------------

    for _, fila in st.session_state.carrito_ingreso.iterrows():

        id_producto = (
            f"{fila['Colegio']}_"
            f"{fila['Articulo']}_"
            f"{fila['Talla']}"
        )

        cantidad_ingresada = int(
            fila["Cantidad"]
        )

        indice = df_inventario[
            df_inventario["ID_BUSQUEDA"]
            .astype(str)
            .eq(id_producto)
        ].index[0]

        df_inventario.loc[
            indice,
            "INVENTARIO"
        ] = (
            int(
                df_inventario.loc[
                    indice,
                    "INVENTARIO"
                ]
            )
            + cantidad_ingresada
        )

    # ------------------------------------------
    # GUARDAR INVENTARIO
    # ------------------------------------------

    df_inventario.to_csv(
        "tablas/inventario.csv",
        sep=";",
        index=False
    )

    # ------------------------------------------
    # LIMPIAR CARRITO
    # ------------------------------------------

    st.session_state.carrito_ingreso = pd.DataFrame(
        columns=[
            "Eliminar",
            "Colegio",
            "Articulo",
            "Talla",
            "Cantidad",
            "Costo Unitario",
            "Subtotal"
        ]
    )

    st.success(
        "Mercancía ingresada correctamente al inventario."
    )

    st.rerun()