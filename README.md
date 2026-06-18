# Proyecto de ventas DYUNIC

Aplicacion Streamlit para registrar ventas, gestionar carritos, consultar inventario y revisar resumenes de facturacion de DYUNIC.

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

- `streamlit_app.py`: vista principal de ventas.
- `pages/`: paginas adicionales de ventas, inventario, tablero y estados financieros.
- `tablas/`: archivos CSV usados por la app.
- `scripts de limpieza/`: notebooks y scripts para preparar datos.
