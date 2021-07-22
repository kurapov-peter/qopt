import relops
from device import Device
import networkx as nx
import graph_utils


class PlanNode(object):
    def __init__(self, op: relops.Operator, dev: Device):
        self._op = op
        self._dev = dev

    @property
    def device(self):
        return self._dev

    def __repr__(self):
        return self._op.__repr__() + ' ' + self._dev.__repr__()

    def __str__(self):
        return self._op.__repr__() + ' ' + self._dev.__repr__()

    def is_router(self):
        return isinstance(self._op, relops.Router)


class Plan(object):
    def __init__(self, graph: nx.DiGraph):
        self._g = graph

    def get_routers(self):
        graph_utils.get_routers(self._g)

