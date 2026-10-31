import unittest
from datetime import date

import pandas as pd

from production_forecast import calculate_order, monthly_estimate


class ForecastTests(unittest.TestCase):
    def setUp(self):
        self.key = dict(school_norm='colegio', product_norm='blusa', size_norm='6', familia_produccion='blusa')
        self.sales = pd.DataFrame([dict(self.key, year=y, month=1, qty=q)
                                   for y, q in [(2024, 10), (2025, 20), (2026, 30)]])
        self.inventory = pd.DataFrame([dict(self.key, stock=0)])

    def test_weights_and_growth(self):
        self.assertAlmostEqual(monthly_estimate(self.sales, self.key, 2027, 1), 25.3)

    def test_missing_year_and_new_product(self):
        missing = self.sales[self.sales.year.ne(2025)]
        self.assertAlmostEqual(monthly_estimate(missing, self.key, 2027, 1), 18.7)
        new = self.sales[self.sales.year.eq(2026)]
        self.assertAlmostEqual(monthly_estimate(new, self.key, 2027, 1), 33)

    def test_remaining_sales_and_closed_season(self):
        sales = pd.concat([self.sales, pd.DataFrame([dict(self.key, year=2027, month=1, qty=10)])])
        detail = calculate_order(sales, self.inventory, 2027, [1, 2], date(2027, 1, 15))
        self.assertEqual(detail.iloc[0].demanda_pendiente, 15)
        closed = calculate_order(sales, self.inventory, 2027, [1, 2], date(2027, 3, 1))
        self.assertEqual(closed.orden_produccion.sum(), 0)

    def test_inventory_and_shared_batch(self):
        other = dict(self.key, school_norm='otro')
        sales = pd.concat([self.sales, self.sales.assign(school_norm='otro')])
        inventory = pd.DataFrame([dict(self.key, stock=26), dict(other, stock=26)])
        detail = calculate_order(sales, inventory, 2027, [1, 2], date(2027, 1, 1))
        self.assertEqual(detail.orden_sin_redondeo.sum(), 4)
        self.assertEqual(detail.orden_produccion.sum(), 5)
        self.assertTrue((detail.orden_produccion >= detail.orden_sin_redondeo).all())


if __name__ == '__main__':
    unittest.main()
