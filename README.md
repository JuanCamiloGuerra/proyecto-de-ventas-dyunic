# Proyecto de ventas DYUNIC

Aplicacion Streamlit para registrar ventas, controlar inventario, consultar tableros y revisar informacion comercial de DYUNIC.

El proyecto trabaja principalmente con archivos CSV ubicados en `tablas/`. La app esta pensada para operacion diaria: vender, ingresar mercancia, ajustar inventario, revisar existencias y analizar ventas.

## Ejecutar en local

1. Instalar dependencias:

```bash
pip install -r requirements.txt
```

2. Ejecutar la app:

```bash
streamlit run streamlit_app.py
```

## Estructura principal

- `streamlit_app.py`: vista principal de venta con carrito, medios de pago, registro de ventas, facturacion e impacto al inventario.
- `pages/`: paginas adicionales de venta, inventario, tableros y revision.
- `tablas/`: archivos CSV usados como fuente de datos y almacenamiento operativo.
- `scripts de limpieza/`: notebooks para limpiar y preparar datos historicos.
- `.devcontainer/`: configuracion para GitHub Codespaces.

## Paginas de la app

### `streamlit_app.py`

Vista principal de ventas. Permite seleccionar colegio, articulo, talla y cantidad; agregar productos al carrito; registrar medios de pago; cerrar la venta; descontar inventario; guardar detalle en `ventas_df.csv`; guardar factura en `facturacion_ventas.csv`; y mostrar los ultimos registros de ventas y facturacion.

### `pages/P1_ventas_1.py`

Vista adicional de ventas con carrito independiente. Usa llaves propias de Streamlit (`p1_...`) para que sus inputs, botones y carrito no se crucen con la vista principal ni con otras paginas.

### `pages/P2_ventas_2.py`

Segunda vista de ventas con carrito e inputs independientes (`p2_...`). Sirve para operar otra pantalla de venta sin mezclar datos de sesion con `P1` o con `streamlit_app.py`.

### `pages/P3_tablero_resumen_ventas.py`

Tablero de resumen de ventas basado en `tablas/facturacion_ventas.csv`. Incluye filtros por año, mes y dia, con opcion `Todos` para el filtro de dia. Calcula total vendido y total pendiente, muestra resumen por fecha y seccion de productos pendientes por entregar.

### `pages/P4.1_ingreso_mercancia.py`

Pagina para ingresar mercancia al inventario. Permite armar un carrito de ingreso, sumar cantidades al `inventario.csv` y guardar un historial en `tablas/ingreso_mercancia_registro.csv`.

El registro de ingreso guarda:

- `fecha`: formato largo, por ejemplo `jueves, 18 de junio de 2026`.
- `dia`, `mes`, `año`
- `hora`
- `colegio`
- `PRODUCTO`
- `TALLA`
- `VALOR`
- `Cantidad`
- `Subtotal`
- `ID_BUSQUEDA`

Al final de la pagina se muestra una vista con los ultimos registros de ingreso de mercancia.

### `pages/P4.2_ajuste_inventario.py`

Pagina para registrar ajustes de inventario. Permite seleccionar producto, motivo de ajuste y cantidad, aplicar el movimiento al inventario y guardar trazabilidad en `tablas/ajustes_inventario_registro.csv`.

### `pages/P4.3_revisar_inventario.py`

Monitor de inventario. Permite filtrar y revisar existencias por colegio, producto y talla para consultar rapidamente el estado actual de inventario.

### `pages/P4.3.1_top ventas.py`

Dashboard de top ventas basado exclusivamente en `tablas/ventas_df.csv`. Incluye filtros con opcion `Todos` para:

- Año
- Mes
- Dia
- Colegio
- Articulo
- Talla

Muestra metricas de unidades vendidas, facturas y productos unicos. Incluye rankings por producto, colegio, articulo y talla. Actualmente el dashboard esta enfocado en unidades, sin valores monetarios.

### `pages/P4.4_ajustar_saldos.py`

Pagina reservada para trabajo futuro. Actualmente esta vacia.

### `pages/P5_estados_financieros.py`

Pagina de revision de ventas. Incluye filtros y una tabla de ventas encontradas para analizar registros desde la informacion disponible.

## Archivos de datos importantes

- `tablas/ventas_df.csv`: detalle de productos vendidos por factura.
- `tablas/facturacion_ventas.csv`: resumen de facturacion y pagos.
- `tablas/inventario.csv`: inventario actual por `ID_BUSQUEDA`.
- `tablas/ingreso_mercancia_registro.csv`: historial de ingresos de mercancia.
- `tablas/ajustes_inventario_registro.csv`: historial de ajustes de inventario.
- `tablas/colegios.csv`, `tablas/tallas.csv`, `tablas/precios.csv`: tablas auxiliares para formularios y calculos.

## Limpieza de datos

La carpeta `scripts de limpieza/` contiene notebooks para preparar datos historicos. Actualmente incluye:

- `limpiar_facturacion_ventas_numeros.ipynb`: limpia columnas numericas en `facturacion_ventas.csv`, especialmente valores que aparecen como `54000.0` y deben quedar como `54000`.

El notebook tambien contempla columnas usadas por el tablero de ventas, como `total efectivo`, `total tarjeta`, `total transfencia` y `total pendiente`.

## Notas de operacion

- Antes de registrar ventas o ingresos, revisar que `ID_BUSQUEDA` no este duplicado en inventario.
- Los archivos CSV son la fuente de datos principal; evitar editarlos manualmente mientras la app esta corriendo.
- Si se cargan datos historicos nuevos, ejecutar primero los notebooks de limpieza correspondientes.
- Despues de cambios importantes en datos o codigo, guardar en Git y subir a GitHub.
