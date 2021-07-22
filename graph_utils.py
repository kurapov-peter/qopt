import networkx as nx
import matplotlib.pyplot as plt
from plan import PlanNode
from device import *
import relops


def display(g: nx.DiGraph):
    pos = nx.spring_layout(g, seed=6)
    nx.draw(g, pos, with_labels=True, font_weight='bold')
    nx.draw_networkx_edge_labels(g, pos)
    plt.show()


def draw_graph_write_dot(g, name):
    from networkx.drawing.nx_pydot import write_dot
    pos = nx.nx_agraph.graphviz_layout(g)
    nx.draw(g, pos=pos)
    write_dot(g, name + '.dot')


def get_het_graph_for(op: relops.Operator) -> nx.DiGraph:
    """
    CPU/GPU schema only
    :param op:
    :return:
    """
    g = nx.DiGraph()
    cpu_op = PlanNode(op, CPU())
    gpu_op = PlanNode(op, GPU())
    router = PlanNode(relops.Router(), CPU())
    dummy = PlanNode(relops.Dummy(), CPU())
    mm1 = PlanNode(relops.MemCpy(), CPU())
    mm2 = PlanNode(relops.MemCpy(), CPU())
    cpu2gpu = PlanNode(relops.CPU2GPU(), CPU())
    gpu2cpu = PlanNode(relops.GPU2CPU(), CPU())

    g.add_nodes_from([cpu_op, gpu_op, router, dummy, mm1, mm2, cpu2gpu, gpu2cpu])
    g.add_edges_from([(router, mm1), (router, mm2), (mm1, cpu_op), (cpu_op, dummy), (mm2, cpu2gpu), (cpu2gpu, gpu_op),
                      (gpu_op, gpu2cpu), (gpu2cpu, dummy)])
    assert nx.is_directed_acyclic_graph(g)
    return g


def get_het_graph_for_join(op: relops.RelJoin) -> nx.DiGraph:
    g = nx.DiGraph()
    cpu_op = PlanNode(op, CPU())
    gpu_op = PlanNode(op, GPU())
    router_a = PlanNode(relops.Router(), CPU())
    router_b = PlanNode(relops.Router(), CPU())
    mms = [PlanNode(relops.MemCpy(), CPU()) for _ in range(4)]
    cpu2gpu_a = PlanNode(relops.CPU2GPU(), CPU())
    cpu2gpu_b = PlanNode(relops.CPU2GPU(), CPU())
    gpu2cpu = PlanNode(relops.GPU2CPU(), CPU())
    dummy = PlanNode(relops.Dummy(), CPU())

    g.add_nodes_from([cpu_op, gpu_op, router_a, router_b, cpu2gpu_a, cpu2gpu_b, gpu2cpu, dummy])
    g.add_nodes_from(mms)

    g.add_edges_from([(router_a, mms[0]), (router_a, mms[1]), (mms[0], cpu_op), (cpu_op, dummy), (mms[1], cpu2gpu_a),
                      (cpu2gpu_a, gpu_op), (gpu_op, gpu2cpu), (gpu2cpu, dummy), (router_b, mms[2]), (router_b, mms[3]),
                      (mms[3], cpu2gpu_b), (cpu2gpu_b, gpu_op), (mms[2], cpu_op)])
    assert nx.is_directed_acyclic_graph(g)
    return g


def sources(g: nx.DiGraph):
    return [node for node, deg in g.in_degree() if deg == 0]


def drains(g: nx.DiGraph):
    return [node for node, deg in g.out_degree() if deg == 0]


def get_routers(g: nx.DiGraph):
    return [node for node in g if node.is_router()]
