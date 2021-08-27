from device import Device, CPU
import relops
import networkx as nx
import graph_utils
from estimator import cost, join_cost, DataParams


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
    def props(self) -> dict:
        return self._props

    @props.setter
    def props(self, props: dict):
        self._props = props


class Plan(object):
    def __init__(self, graph: nx.DiGraph):
        self._g = graph
        self._features = {}
        self._update_routers_features()

    def get_routers(self):
        return graph_utils.get_routers(self._g)

    def get_features(self):
        return self._features

    def set_routers_coeffs(self, coeffs: list):
        assert len(coeffs) == len(self.get_routers())
        if not all(0 <= x <= 1 for x in coeffs):
            print(coeffs)
        assert all(0 <= x <= 1 for x in coeffs)
        routers = self.get_routers()
        for i in range(len(coeffs)):
            routers[i].get_op().set_input_coeff({CPU(): coeffs[i]})
        self._update_routers_features()

    def set_routers_use_gpu_only(self):
        routers = self.get_routers()
        self.set_routers_coeffs([0] * len(routers))

    def set_routers_use_cpu_only(self):
        routers = self.get_routers()
        self.set_routers_coeffs([1] * len(routers))

    def cost(self, input_data: dict = None):
        self._cleanup()
        self._update_input_costs(input_data)
        return self._calculate_cost()
        # return sum([cost(x.get_op(), x.device, DataParams.plan_input()) for x in self._g])

    def display(self):
        graph_utils.display(self._g)

    def _update_features(self):
        self._update_routers_features()

    def _update_routers_features(self):
        routers = self.get_routers()
        self._features['routers'] = [router.get_op().get_input_coeff_for_device(router.device) for router in routers]

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

            current_op_cost = 0
            op_input = None
            if predecessors_num == 0:  # sources
                op_input = node.props['input']
                current_op_cost = cost(node.get_op(), node.device, node.props['input'])
            elif isinstance(node.get_op(), relops.RelJoin):
                assert predecessors_num > 1
                pred = list(self._g.predecessors(node))
                op_input = DataParams(pred[0].props['input'].bytes * pred[1].props['input'].bytes)  # fixme
                current_op_cost = join_cost(node.get_op(), node.device,
                                            [v.props['input'] for v in self._g.predecessors(node)])
            elif isinstance(node.get_op(), relops.Router):
                op_input = DataParams(sum(x.props['input'].bytes for x in self._g.predecessors(node)))
                current_op_cost = cost(node.get_op(), node.device, op_input)
            else:
                assert len(list(self._g.predecessors(node))) == 1
                pred = list(self._g.predecessors(node))[0]
                op_input = pred.get_op().input_scale(pred.props["input"], node.device)
                current_op_cost = cost(node.get_op(), node.device, op_input)

            node.props['input'] = op_input
            total_cost += current_op_cost

            for suc in self._g.successors(node):
                if not suc.props['ready'] and all(v.props['ready'] for v in self._g.predecessors(suc)):
                    suc.props['ready'] = True
                    queue.append(suc)
        return total_cost

    def _cleanup(self):
        for node in self._g:
            node.props = {}
