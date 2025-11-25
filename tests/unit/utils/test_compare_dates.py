import unittest
from datetime import datetime

from trade_api.utils import compare_dates


class TestCompareDates(unittest.TestCase):
    def test_both_none(self):
        self.assertTrue(compare_dates(None, None))

    def test_first_none(self):
        self.assertTrue(compare_dates(None, datetime(2025, 11, 25)))

    def test_second_none(self):
        self.assertTrue(compare_dates(datetime(2025, 11, 25), None))

    def test_date1_less_than_date2(self):
        self.assertTrue(compare_dates(datetime(2025, 11, 24), datetime(2025, 11, 25)))

    def test_date1_equal_date2(self):
        self.assertTrue(compare_dates(datetime(2025, 11, 25), datetime(2025, 11, 25)))

    def test_date1_greater_than_date2(self):
        self.assertFalse(compare_dates(datetime(2025, 11, 26), datetime(2025, 11, 25)))
