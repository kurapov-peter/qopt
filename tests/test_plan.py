from unittest import TestCase
from data_params import DataParams
import relops
import graph_utils
from plan import Plan


class TestPlan(TestCase):
    def test_get_routers(self):
        self.fail()

    def test_features(self):
        self.fail()

    def test_cost(self):
        self.fail()

    def test__update_input_costs(self):
        self.fail()

    def test__calculate_cost(self):
        self.fail()

    def test__cleanup(self):
        self.fail()

    def test_set_routers_coeffs(self):
        a_data = DataParams(100)
        b_data = DataParams(500)
        scan_a = graph_utils.get_het_graph_for(relops.RelScan("A", a_data))
        scan_b = graph_utils.get_het_graph_for(relops.RelScan("B", b_data))
        join = graph_utils.get_het_graph_for(relops.RelJoin())
        res = graph_utils.connect_join(scan_a, scan_b, join)
        final = graph_utils.finalize_graph_with(res, relops.RelSort())
        p = Plan(final)
        p._update_routers_features()
        features = p.get_features()['routers']
        self.assertEqual(len(p.get_routers()), len(features))
        self.assertTrue(all(feature == 0 for feature in features))
        p.set_routers_coeffs([1 for _ in features])
        p._update_routers_features()
        features = p.get_features()['routers']
        self.assertEqual(len(p.get_routers()), len(features))
        self.assertTrue(all(feature == 1 for feature in features))


