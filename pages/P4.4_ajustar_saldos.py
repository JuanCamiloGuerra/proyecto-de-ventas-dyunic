from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st


FACTURACION_PATH = "tablas/facturacion_ventas.csv"
INFO_FACTURAS_PATH = "tablas/info facturas.csv"
TODOS = "Todos"
BOGOTA_TZ = ZoneInfo("America/Bogota")

COLUMNAS_FILTRO = [
    "Día",
    "Mes",
    "Año",
    "Nombre cliente",
    "Numero de contacto",
]

COLUMNAS_VISTA = [
    "ID unico de factura",
    "fecha de venta",
    "Día",
    "Mes",
    "Año",
    "Nombre cliente",
    "Numero de contacto",
    "ID cliente",
    "pago efectivo",
    "pago tarjeta",
    "pago transferencia",
    "valor factura",
    "pendiente",
    "fecha de pago 2",
    "pago efectivo 2",
    "pago tarjeta 2",
    "pago transferencia 2",
    "Estado de factura",
    "total efectivo",
    "total tarjeta",
    "total transfencia",
    "total pendiente",
    "Producto pendiente por entregar",
]


st.set_page_config(
    page_title="Ajustar saldos",
    page_icon="💳",
    layout="wide",
)

st.title("💳 Ajustar saldos y segundos pagos")


@st.cache_data
def cargar_facturacion():
    df = pd.read_csv(
        FACTURACION_PATH,
        sep=";",
        dtype=str,
        keep_default_na=False,
    )

    df.columns = df.columns.str.strip()
    return df


@st.cache_data
def cargar_estados_factura():
    df_estados = pd.read_csv(
        INFO_FACTURAS_PATH,
        sep=";",
        header=None,
        dtype=str,
        keep_default_na=False,
    )

    estados = (
        df_estados.iloc[:, 0]
        .astype(str)
        .str.strip()
    )

    return [
        estado for estado in estados.tolist()
        if estado != ""
    ]


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

    return pd.to_numeric(texto, errors="coerce")


def numero(valor):
    valor_limpio = limpiar_numero(valor)
    if pd.isna(valor_limpio):
        return 0
    return int(valor_limpio)


def opciones_con_todos(serie, numerico=False):
    valores = serie.astype(str).str.strip()
    valores = valores[valores != ""]

    if numerico:
        valores = (
            pd.to_numeric(valores, errors="coerce")
            .dropna()
            .astype(int)
            .unique()
            .tolist()
        )
        return [TODOS] + sorted(valores)

    return [TODOS] + sorted(valores.unique().tolist())


def aplicar_filtro(df, columna, seleccion):
    if TODOS in seleccion or not seleccion:
        return df

    if columna in ["Día", "Mes", "Año"]:
        valores = [int(valor) for valor in seleccion]
        return df[pd.to_numeric(df[columna], errors="coerce").isin(valores)]

    return df[df[columna].astype(str).str.strip().isin(seleccion)]


def fecha_larga_actual():
    ahora = datetime.now(BOGOTA_TZ)
    dias_semana = [
        "lunes",
        "martes",
        "miércoles",
        "jueves",
        "viernes",
        "sábado",
        "domingo",
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
        "diciembre",
    ]

    return (
        f"{dias_semana[ahora.weekday()]}, "
        f"{ahora.day} de "
        f"{meses_texto[ahora.month]} de "
        f"{ahora.year}"
    )


def segundo_pago_registrado(row):
    return any(
        numero(row[columna]) != 0
        for columna in [
            "pago efectivo 2",
            "pago tarjeta 2",
            "pago transferencia 2",
        ]
    )


def agregar_alerta_saldo(df):
    df_alertas = df.copy()

    for columna in [
        "pago efectivo 2",
        "pago tarjeta 2",
        "pago transferencia 2",
        "total pendiente",
    ]:
        df_alertas[columna] = (
            df_alertas[columna]
            .map(numero)
        )

    df_alertas["ALERTA SALDO"] = df_alertas.apply(
        lambda row: (
            "REVISAR"
            if abs(row["total pendiente"]) > 5000
            and (
                row["pago efectivo 2"] != 0
                or row["pago tarjeta 2"] != 0
                or row["pago transferencia 2"] != 0
            )
            else ""
        ),
        axis=1,
    )

    return df_alertas


def resaltar_alerta(row):
    if row.get("ALERTA SALDO") == "REVISAR":
        return ["background-color: #B7791F; color: #111827"] * len(row)
    return [""] * len(row)


def anio_maximo(df):
    anios = (
        pd.to_numeric(df["Año"], errors="coerce")
        .dropna()
        .astype(int)
    )

    if anios.empty:
        return TODOS

    return int(anios.max())


df_facturacion = cargar_facturacion()
estados_factura = cargar_estados_factura()

for columna in COLUMNAS_FILTRO:
    if columna not in df_facturacion.columns:
        st.error(f"No existe la columna requerida: {columna}")
        st.stop()

st.header("Filtros")

col1, col2, col3 = st.columns(3)
col4, col5 = st.columns(2)

df_filtrado = df_facturacion.copy()

with col1:
    opciones_anio = opciones_con_todos(df_filtrado["Año"], numerico=True)
    anio_default = anio_maximo(df_filtrado)

    if anio_default not in opciones_anio:
        anio_default = TODOS

    filtro_anio = st.multiselect(
        "Año",
        opciones_anio,
        default=[anio_default],
        key="ajuste_saldos_anio",
    )

df_filtrado = aplicar_filtro(df_filtrado, "Año", filtro_anio)

with col2:
    filtro_mes = st.multiselect(
        "Mes",
        opciones_con_todos(df_filtrado["Mes"], numerico=True),
        default=[TODOS],
        key="ajuste_saldos_mes",
    )

df_filtrado = aplicar_filtro(df_filtrado, "Mes", filtro_mes)

with col3:
    filtro_dia = st.multiselect(
        "Día",
        opciones_con_todos(df_filtrado["Día"], numerico=True),
        default=[TODOS],
        key="ajuste_saldos_dia",
    )

df_filtrado = aplicar_filtro(df_filtrado, "Día", filtro_dia)

with col4:
    filtro_nombre = st.multiselect(
        "Nombre cliente",
        opciones_con_todos(df_filtrado["Nombre cliente"]),
        default=[TODOS],
        key="ajuste_saldos_nombre_cliente",
    )

df_filtrado = aplicar_filtro(df_filtrado, "Nombre cliente", filtro_nombre)

with col5:
    filtro_contacto = st.multiselect(
        "Numero de contacto",
        opciones_con_todos(df_filtrado["Numero de contacto"]),
        default=[TODOS],
        key="ajuste_saldos_numero_contacto",
    )

df_filtrado = aplicar_filtro(df_filtrado, "Numero de contacto", filtro_contacto)

st.divider()

if df_filtrado.empty:
    st.warning("No hay facturas para los filtros seleccionados.")
    st.stop()

columnas_disponibles = [
    columna for columna in COLUMNAS_VISTA
    if columna in df_filtrado.columns
]

df_vista = agregar_alerta_saldo(
    df_filtrado[columnas_disponibles]
)

st.subheader("Facturas filtradas")

max_styled_cells = 262144
total_cells = df_vista.shape[0] * df_vista.shape[1]

if total_cells <= max_styled_cells:
    st.dataframe(
        df_vista.style.apply(resaltar_alerta, axis=1),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info(
        "La tabla filtrada es muy grande para aplicar colores. "
        "Reduce los filtros para ver el resaltado de alertas."
    )

    st.dataframe(
        df_vista,
        use_container_width=True,
        hide_index=True,
    )

alertas = df_vista[df_vista["ALERTA SALDO"] == "REVISAR"]

if not alertas.empty:
    st.error(
        f"Hay {len(alertas)} factura(s) con segundo pago registrado "
        "y diferencia absoluta mayor a $5,000."
    )

st.divider()

st.header("Seleccionar factura a editar")

df_selector = df_filtrado.reset_index().copy()
df_selector["opcion"] = (
    df_selector["ID unico de factura"].astype(str)
    + " | "
    + df_selector["Nombre cliente"].astype(str)
    + " | "
    + df_selector["Numero de contacto"].astype(str)
    + " | pendiente: "
    + df_selector["pendiente"].astype(str)
)

opcion_factura = st.selectbox(
    "Factura",
    df_selector["opcion"].tolist(),
    key="ajuste_saldos_factura",
)

fila_seleccionada = df_selector[
    df_selector["opcion"] == opcion_factura
].iloc[0]

indice_original = int(fila_seleccionada["index"])

st.caption(
    f"Factura seleccionada: {fila_seleccionada['ID unico de factura']}"
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    nuevo_pago_efectivo_2 = st.number_input(
        "Efectivo",
        min_value=0,
        value=0,
        step=1000,
        key=f"ajuste_saldos_pago_efectivo_2_{indice_original}",
    )

with col2:
    nuevo_pago_tarjeta_2 = st.number_input(
        "Tarjeta",
        min_value=0,
        value=0,
        step=1000,
        key=f"ajuste_saldos_pago_tarjeta_2_{indice_original}",
    )

with col3:
    nuevo_pago_transferencia_2 = st.number_input(
        "Transferencia",
        min_value=0,
        value=0,
        step=1000,
        key=f"ajuste_saldos_pago_transferencia_2_{indice_original}",
    )

estado_actual = str(
    fila_seleccionada.get("Estado de factura", "")
).strip()

if estado_actual not in estados_factura and estados_factura:
    estados_para_select = [estado_actual] + estados_factura
else:
    estados_para_select = estados_factura

with col4:
    estado_factura = st.selectbox(
        "Estado de factura",
        estados_para_select,
        index=(
            estados_para_select.index(estado_actual)
            if estado_actual in estados_para_select
            else 0
        ),
        key="ajuste_saldos_estado_factura",
    )

pago_efectivo_1 = numero(fila_seleccionada["pago efectivo"])
pago_tarjeta_1 = numero(fila_seleccionada["pago tarjeta"])
pago_transferencia_1 = numero(fila_seleccionada["pago transferencia"])
pago_efectivo_2_actual = numero(fila_seleccionada.get("pago efectivo 2", 0))
pago_tarjeta_2_actual = numero(fila_seleccionada.get("pago tarjeta 2", 0))
pago_transferencia_2_actual = numero(
    fila_seleccionada.get("pago transferencia 2", 0)
)
valor_factura = numero(fila_seleccionada["valor factura"])

pago_efectivo_2_acumulado = int(
    pago_efectivo_2_actual
    + nuevo_pago_efectivo_2
)
pago_tarjeta_2_acumulado = int(
    pago_tarjeta_2_actual
    + nuevo_pago_tarjeta_2
)
pago_transferencia_2_acumulado = int(
    pago_transferencia_2_actual
    + nuevo_pago_transferencia_2
)

total_efectivo = int(pago_efectivo_1 + pago_efectivo_2_acumulado)
total_tarjeta = int(pago_tarjeta_1 + pago_tarjeta_2_acumulado)
total_transferencia = int(
    pago_transferencia_1
    + pago_transferencia_2_acumulado
)
total_pendiente = int(
    valor_factura
    - total_efectivo
    - total_tarjeta
    - total_transferencia
)

st.subheader("Resultado calculado")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total efectivo", f"${total_efectivo:,.0f}")

with col2:
    st.metric("Total tarjeta", f"${total_tarjeta:,.0f}")

with col3:
    st.metric("Total transferencia", f"${total_transferencia:,.0f}")

with col4:
    st.metric("Total pendiente", f"${total_pendiente:,.0f}")

segundo_pago_no_cero = (
    pago_efectivo_2_acumulado != 0
    or pago_tarjeta_2_acumulado != 0
    or pago_transferencia_2_acumulado != 0
)

if abs(total_pendiente) > 5000 and segundo_pago_no_cero:
    st.error(
        "Alerta: el valor absoluto de total pendiente es mayor a $5,000 "
        "con segundo pago registrado."
    )

st.divider()

guardar = st.button(
    "💾 Registrar segundo pago",
    use_container_width=True,
    key="ajuste_saldos_guardar",
)

if guardar:
    df_actualizado = df_facturacion.copy()

    df_actualizado.loc[indice_original, "fecha de pago 2"] = fecha_larga_actual()
    df_actualizado.loc[indice_original, "pago efectivo 2"] = (
        pago_efectivo_2_acumulado
    )
    df_actualizado.loc[indice_original, "pago tarjeta 2"] = (
        pago_tarjeta_2_acumulado
    )
    df_actualizado.loc[indice_original, "pago transferencia 2"] = (
        pago_transferencia_2_acumulado
    )
    df_actualizado.loc[indice_original, "Estado de factura"] = estado_factura

    df_actualizado.loc[indice_original, "total efectivo"] = total_efectivo
    df_actualizado.loc[indice_original, "total tarjeta"] = total_tarjeta
    df_actualizado.loc[indice_original, "total transfencia"] = total_transferencia
    df_actualizado.loc[indice_original, "total pendiente"] = total_pendiente

    df_actualizado.to_csv(
        FACTURACION_PATH,
        sep=";",
        index=False,
        encoding="utf-8",
    )

    cargar_facturacion.clear()

    st.success("Segundo pago registrado correctamente.")
    st.rerun()
