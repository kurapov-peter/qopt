import networkx as nx
import relops
from device import Device
import graph_utils
from plan import Plan
from data_params import DataParams
from optimizer import optimize, genetic_search


if __name__ == '__main__':
    a_data = DataParams(100)
    b_data = DataParams(500)
    scan_a = graph_utils.get_het_graph_for(relops.RelScan("A", a_data))
    scan_b = graph_utils.get_het_graph_for(relops.RelScan("B", b_data))
    join = graph_utils.get_het_graph_for(relops.RelJoin())
    res = graph_utils.connect_join(scan_a, scan_b, join)
    final = graph_utils.finalize_graph_with(res, relops.RelSort())
    # graph_utils.display(final)
    p = Plan(final)
    print('Initial const: ', p.cost())

    coeffs_len = len(p.get_features()['routers'])
    p.set_routers_use_cpu_only()
    print('All cpu cost: ', p.cost())
    p.set_routers_use_gpu_only()
    print('All gpu cost: ', p.cost())

    optimize(p)

    p.set_routers_coeffs([1 for _ in range(coeffs_len)])
    # print(p.cost())

    genetic_search(p)

