from unittest import TestCase
import graph_utils
import networkx as nx
import relops
from plan import PlanNode, Plan
from device import CPU
from data_params import DataParams


class Test(TestCase):
    def test_sources(self):
        g = nx.DiGraph()
        g.add_nodes_from([1, 2, 3])
        g.add_edges_from([(1, 2), (2, 3)])
        self.assertEqual([1], graph_utils.sources(g))

    def test_drains(self):
        g = nx.DiGraph()
        g.add_nodes_from([1, 2, 3])
        g.add_edges_from([(1, 2), (2, 3)])
        self.assertEqual([3], graph_utils.drains(g))

    def test_get_routers(self):
        g = nx.DiGraph()
        g.add_nodes_from([PlanNode(relops.RelJoin(), CPU())])
        self.assertEqual(0, len(graph_utils.get_routers(g)))
        g.add_nodes_from([PlanNode(relops.Router(), CPU())])
        self.assertEqual(1, len(graph_utils.get_routers(g)))

    def test_get_routers_consistent(self):
        a_data = DataParams(100)
        b_data = DataParams(500)
        scan_a = graph_utils.get_het_graph_for(relops.RelScan("A", a_data))
        scan_b = graph_utils.get_het_graph_for(relops.RelScan("B", b_data))
        join = graph_utils.get_het_graph_for(relops.RelJoin())
        res = graph_utils.connect_join(scan_a, scan_b, join)
        final = graph_utils.finalize_graph_with(res, relops.RelSort())
        routers = []
        for i in range(20):
            routers.append(graph_utils.get_routers(final))
        for i in range(20):
            self.assertEqual(routers[0], routers[i])
