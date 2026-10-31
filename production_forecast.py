import calendar
import math

import pandas as pd

KEYS = ['school_norm', 'product_norm', 'size_norm', 'familia_produccion']
WEIGHTS = (0.5, 0.3, 0.2)
GROWTH = 0.10


def monthly_estimate(sales, key, year, month):
    history = sales[sales.year < year]
    for column in KEYS:
        history = history[history[column].eq(key[column])]
    positive = history[history.qty > 0]
    if positive.empty:
        return 0.0
    first = min(zip(positive.year, positive.month))
    values = history[history.month.eq(month)].groupby('year').qty.sum()
    samples = [(max(0.0, float(values.get(year - age, 0))), weight)
               for age, weight in enumerate(WEIGHTS, 1)
               if (year - age, month) >= first]
    if not samples:
        return 0.0
    return sum(value * weight for value, weight in samples) / sum(w for _, w in samples) * (1 + GROWTH)


def units(value):
    return max(0, int(math.floor(value + 0.5)))


def calculate_order(sales, inventory, year, months, today, safety_rate=0.10):
    keys = inventory[KEYS].drop_duplicates().sort_values(KEYS)
    rows = []
    for key in keys.to_dict('records'):
        selected = sales
        stock_rows = inventory
        for column in KEYS:
            selected = selected[selected[column].eq(key[column])]
            stock_rows = stock_rows[stock_rows[column].eq(key[column])]
        forecast = 0.0
        remaining = 0.0
        sold = 0.0
        for month in months:
            estimate = monthly_estimate(selected, key, year, month)
            actual = max(0.0, selected[selected.year.eq(year) & selected.month.eq(month)].qty.sum())
            forecast += estimate
            sold += actual
            if (year, month) >= (today.year, today.month):
                remaining += max(0.0, estimate - actual)
        bridge = 0.0
        # Reserve expected sales before the target season, including the remaining current month.
        cursor_year, cursor_month = today.year, today.month
        while (cursor_year, cursor_month) < (year, min(months)):
            estimate = monthly_estimate(selected, key, cursor_year, cursor_month)
            if (cursor_year, cursor_month) == (today.year, today.month):
                days = calendar.monthrange(cursor_year, cursor_month)[1]
                estimate *= (days - today.day) / days
            bridge += estimate
            cursor_year, cursor_month = (cursor_year + 1, 1) if cursor_month == 12 else (cursor_year, cursor_month + 1)
        stock = units(stock_rows.stock.clip(lower=0).sum())
        available = max(0, stock - units(bridge))
        safety = units(remaining * safety_rate)
        need = max(0, units(remaining) + safety - available)
        rows.append(dict(colegio=key['school_norm'], articulo=key['product_norm'],
                         familia_produccion=key['familia_produccion'],
                         colegio_prenda=f"{key['school_norm']} | {key['product_norm']}", talla=key['size_norm'],
                         inventario=stock, consumo_pretemporada=units(bridge), inventario_disponible=available,
                         pronostico_cierre=units(forecast), vendido_temporada=units(sold),
                         demanda_pendiente=units(remaining), stock_minimo=safety,
                         orden_sin_redondeo=need, orden_produccion=need))
    detail = pd.DataFrame(rows)
    if detail.empty:
        return detail
    # Allocate only the batch remainder, preserving the SKU needs and all view totals.
    for _, group in detail.groupby(['familia_produccion', 'talla'], sort=True):
        total = int(group.orden_sin_redondeo.sum())
        if total:
            extra = (-total) % 5
            index = group.orden_sin_redondeo.idxmax()
            detail.loc[index, 'orden_produccion'] += extra
    return detail


def backtest(sales):
    results = []
    groups = list(sales.groupby(KEYS))
    for year in (2024, 2025, 2026):
        predictions = []
        for values, selected in groups:
            key = dict(zip(KEYS, values))
            history = selected[selected.year < year]
            forecast = units(sum(monthly_estimate(history, key, year, month) for month in (1, 2)))
            actual_rows = selected[selected.year.eq(year) & selected.month.isin([1, 2])]
            actual = units(actual_rows.groupby('month').qty.sum().clip(lower=0).sum())
            predictions.append((forecast, actual))
        for rate in (0.10, 0.15, 0.20):
            predicted_total = actual_total = excess = shortage = 0
            for forecast, actual in predictions:
                planned = forecast + units(forecast * rate)
                predicted_total += planned
                actual_total += actual
                excess += max(0, planned - actual)
                shortage += max(0, actual - planned)
            results.append(dict(año=year, margen=int(rate * 100), previsto=predicted_total,
                                real=actual_total, excedente=excess, faltante=shortage))
    return pd.DataFrame(results)
