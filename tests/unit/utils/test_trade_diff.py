import unittest
from datetime import date

from trade_api.utils import trade_diff


class TestTradeDiff(unittest.TestCase):
    def test_no_difference(self):
        trade1 = {"id": 1, "amount": 100, "trade_date": date(2025, 11, 25)}
        trade2 = {"id": 1, "amount": 100, "trade_date": date(2025, 11, 25)}
        self.assertEqual(trade_diff(trade1, trade2), {})

    def test_difference_in_multiple_fields(self):
        trade1 = {
            "id": 1,
            "amount": 100,
            "type": "buy",
            "trade_date": date(2025, 11, 25),
        }
        trade2 = {
            "id": 2,
            "amount": 200,
            "type": "sell",
            "trade_date": date(2025, 11, 25),
        }
        expected = {
            "id": {"previous": "1", "new": "2"},
            "amount": {"previous": "100", "new": "200"},
            "type": {"previous": "buy", "new": "sell"},
        }
        self.assertEqual(trade_diff(trade1, trade2), expected)

    def test_difference_ignored_for_date_fields(self):
        trade1 = {"id": 1, "trade_date": date(2025, 11, 25)}
        trade2 = {"id": 1, "trade_date": date(2025, 11, 26)}
        self.assertEqual(trade_diff(trade1, trade2), {})
