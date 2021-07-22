from unittest import TestCase
import graph_utils
import networkx as nx
import relops
from plan import PlanNode
from device import CPU


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
