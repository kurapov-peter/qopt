from device import Device
import relops
import networkx as nx
import graph_utils
from estimator import cost, join_cost, DataParams
import math


class PlanNode(object):
    def __init__(self, op: relops.Operator, dev: Device):
        self._op = op
        self._dev = dev
        self._props = {}

    @property
    def device(self):
        return self._dev

    def get_op(self):
        return self._op

    def __repr__(self):
        return self._op.__repr__() + ' ' + self._dev.__repr__()

    def __str__(self):
        return self._op.__repr__() + ' ' + self._dev.__repr__()

    def is_router(self):
        return isinstance(self._op, relops.Router)

    @property
    def props(self):
        return self._props


class Plan(object):
    def __init__(self, graph: nx.DiGraph):
        self._g = graph

    def get_routers(self):
        graph_utils.get_routers(self._g)

    def cost(self, input_data: dict = None):
        self._cleanup()
        self._update_input_costs(input_data)
        return self._calculate_cost()
        # return sum([cost(x.get_op(), x.device, DataParams.plan_input()) for x in self._g])

    def _update_input_costs(self, table_data: dict):
        """
        Set entry routers data to appropriate values depending on input scan tables sizes
        :param table_data: "{Table "A": x bytes, ...}", if empty, uses scan data
        :return:
        """
        for src in graph_utils.sources(self._g):
            for node in nx.dfs_preorder_nodes(self._g, source=src):
                if isinstance(node.get_op(), relops.RelScan):
                    if table_data:
                        src.props['input'] = table_data[node.get_op().table_name()]
                    else:
                        src.props['input'] = node.get_op().table()
                    break

    def _calculate_cost(self):  # todo: refactor me
        total_cost = 0
        queue = graph_utils.sources(self._g)
        # mark sources as ready
        for node in self._g:
            node.props['ready'] = node in queue

        while len(queue):
            node = queue.pop(0)
            predecessors_num = self._g.in_degree(node)

            if predecessors_num == 0:  # sources
                total_cost += cost(node.get_op(), node.device, node.props['input'])
            elif isinstance(node.get_op(), relops.RelJoin):
                assert predecessors_num > 1
                pred = list(self._g.predecessors(node))
                total_input = DataParams(pred[0].props['input'].bytes * pred[1].props['input'].bytes)  # fixme
                node.props['input'] = total_input
                total_cost += join_cost(node.get_op(), node.device,
                                        [v.props['input'] for v in self._g.predecessors(node)])
            elif isinstance(node.get_op(), relops.Router):
                total_input = DataParams(sum(x.props['input'].bytes for x in self._g.predecessors(node)))
                node.props['input'] = total_input
                total_cost += cost(node.get_op(), node.device, total_input)
            else:
                assert predecessors_num == 1
                pred = list(self._g.predecessors(node))
                assert len(pred) == 1
                input = pred[0].get_op().input_scale(pred[0].props["input"], node.device)
                node.props['input'] = input
                total_cost += node.get_op().cost(node.device, pred[0].props["input"])

            for suc in self._g.successors(node):
                if not suc.props['ready'] and all(v.props['ready'] for v in self._g.predecessors(suc)):
                    suc.props['ready'] = True
                    queue.append(suc)
        return total_cost

    def _cleanup(self):
        pass
