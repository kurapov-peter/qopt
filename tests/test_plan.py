from unittest import TestCase
from data_params import DataParams
import relops
import graph_utils
from plan import Plan


class TestPlan(TestCase):
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

    def test_cost(self):
        from device import CPU, GPU
        a_data = DataParams(100)
        scan_a = graph_utils.get_het_graph_for(relops.RelScan("A", a_data))
        final = graph_utils.finalize_graph_with(scan_a, relops.RelSort())
        p = Plan(final)
        p.set_routers_use_cpu_only()
        c = p.cost()
        # inputs are ready here
        cpu_nodes = [node for node in p._g if node.device == CPU()]
        cpu_cost = 0
        for node in cpu_nodes:
            assert not isinstance(node.get_op(), relops.RelJoin)
            if len(list(p._g.predecessors(node))) == 0:
                cpu_cost += node.get_op().cost(node.device, node.props['input'])
            else:
                input = DataParams(sum(x.props['input'].bytes for x in p._g.predecessors(node)))
                cpu_cost += node.get_op().cost(node.device, input)

        self.assertEqual(c, cpu_cost)

        p.set_routers_use_gpu_only()
        c = p.cost()

        gpu_nodes = [node for node in p._g if node.device == GPU()] + graph_utils.get_routers(p._g)

        gpu_cost = 0
        for node in gpu_nodes:
            assert not isinstance(node.get_op(), relops.RelJoin)
            if len(list(p._g.predecessors(node))) == 0:
                gpu_cost += node.get_op().cost(node.device, node.props['input'])
            else:
                input = DataParams(sum(x.props['input'].bytes for x in p._g.predecessors(node)))
                gpu_cost += node.get_op().cost(node.device, input)

        self.assertEqual(c, gpu_cost)

    def test_cost_with_coeffs(self):
        from device import CPU, GPU
        a_data = DataParams(100)
        scan_a = graph_utils.get_het_graph_for(relops.RelScan("A", a_data))
        final = graph_utils.finalize_graph_with(scan_a, relops.RelSort())
        p = Plan(final)
        p.set_routers_use_cpu_only()
        p.cost()
        d = graph_utils.drains(p._g)
        self.assertEqual(len(d), 1)
        d = d[0]
        sort_input = d.props['input']
        self.assertTrue(sort_input)
        features = p.get_features()['routers']
        p.set_routers_coeffs([0.5]*len(features))
        p.cost()
        d2 = graph_utils.drains(p._g)[0]
        sort_input2 = d2.props['input']
        self.assertEqual(sort_input.bytes, sort_input2.bytes)

        p.set_routers_coeffs([0.3] * len(features))
        p.cost()
        d3 = graph_utils.drains(p._g)[0]
        sort_input3 = d3.props['input']
        self.assertEqual(sort_input.bytes, sort_input3.bytes)

    def test_cost_join(self):
        a_data = DataParams(100)
        b_data = DataParams(500)
        scan_a = graph_utils.get_het_graph_for(relops.RelScan("A", a_data))
        scan_b = graph_utils.get_het_graph_for(relops.RelScan("B", b_data))
        join = graph_utils.get_het_graph_for(relops.RelJoin())
        res = graph_utils.connect_join(scan_a, scan_b, join)
        final = graph_utils.finalize_graph_with(res, relops.RelSort())
        p = Plan(final)
        p.set_routers_use_cpu_only()
        p.cost()
        d = graph_utils.drains(p._g)
        self.assertEqual(len(d), 1)
        d = d[0]
        sort_input = d.props['input']
        self.assertTrue(sort_input)

    def test_complex_cost(self):
        a_data = DataParams(100)
        b_data = DataParams(500)
        scan_a = graph_utils.get_het_graph_for(relops.RelScan("A", a_data))
        scan_b = graph_utils.get_het_graph_for(relops.RelScan("B", b_data))
        join = graph_utils.get_het_graph_for(relops.RelJoin())
        res = graph_utils.connect_join(scan_a, scan_b, join)
        final = graph_utils.finalize_graph_with(res, relops.RelSort())
        p = Plan(final)
        # p.display()
        # self.fail()
