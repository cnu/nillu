import unittest

import datetime

from nillu.utils import parse_date, DateParseException, FutureDateException


class ParseDateTestCase(unittest.TestCase):
    def test_parse_today(self):
        pd, resolution = parse_date('today')
        d = datetime.date.today()
        self.assertEqual(d, pd, "today and parsed date isn't equal")
        self.assertEqual(resolution, 'day', "resolution isn't 'day'")

    def test_parse_yesterday(self):
        pd, resolution = parse_date('yesterday')
        d = datetime.date.today() - datetime.timedelta(days=1)
        self.assertEqual(d, pd, "today and parsed date isn't equal")
        self.assertEqual(resolution, 'day', "resolution isn't 'day'")

    def test_parse_correct_date(self):
        pd, resolution = parse_date('2017/04/10')
        d = datetime.date(2017, 4, 10)
        self.assertEqual(d, pd, "'2017/04/10' and parsed date isn't equal")
        self.assertEqual(resolution, 'day', "resolution isn't 'day'")

    def test_parse_incorrect_date(self):
        with self.assertRaises(DateParseException):
            pd, resolution = parse_date('2017/04/31')

    def test_parse_future_date(self):
        with self.assertRaises(FutureDateException):
            dt = datetime.date.today() + datetime.timedelta(days=1)
            dt_str = dt.strftime('%Y/%m/%d')
            pd, resolution = parse_date(dt_str)

    def test_parse_correct_month(self):
        pd, resolution = parse_date('2017/04')
        d = datetime.date(2017, 4, 1)
        self.assertEqual(d, pd, "'2017/04' and parsed date isn't equal")
        self.assertEqual(resolution, 'month', "resolution isn't 'month'")

    def test_parse_correct_year(self):
        pd, resolution = parse_date('2017')
        d = datetime.date(2017, 1, 1)
        self.assertEqual(d, pd, "'2017' and parsed date isn't equal")
        self.assertEqual(resolution, 'year', "resolution isn't 'year'")

    def test_parse_incorrect_month(self):
        with self.assertRaises(DateParseException):
            pd, resolution = parse_date('2017/13')

    def test_parse_incorrect_year(self):
        with self.assertRaises(DateParseException):
            pd, resolution = parse_date('10000')

    def test_parse_3_slashes(self):
        """parse dates with more than 2 slashes"""
        pd, resolution = parse_date('2017/04/15/20')
        d = datetime.date.today()
        self.assertEqual(d, pd)
        self.assertEqual(resolution, 'day', "resolution isn't 'day'")
