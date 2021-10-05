from unittest import TestCase
from data_params import Table
import pandas as pd


class TestTable(TestCase):
    def test_bytes(self):
        t = Table('test', pd.DataFrame({'idx': [1, 2], 'data': [3, 4]}))
        self.assertEqual(4*64, t.bytes())
        t.data = pd.DataFrame({'a': [1, 2, 3, 4], 'b': [3, 4, 5, 6], 'c': [1, 1, 1, 1]})
        self.assertEqual(3*4*64, t.bytes())

    def test_empty(self):
        t = Table('test')
        self.assertTrue(t.empty())
        df = pd.DataFrame({'a': [], 'b': []})
        t.data = df
        self.assertTrue(t.empty())
