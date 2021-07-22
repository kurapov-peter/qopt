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
    if isinstance(op, relops.RelJoin):
        return get_het_graph_for_join(op)
    cpu = CPU()
    gpu = GPU()
    g = nx.DiGraph()
    cpu_op = PlanNode(op, cpu)
    gpu_op = PlanNode(op, gpu)
    router = PlanNode(relops.Router(), cpu)
    dummy = PlanNode(relops.Dummy(), cpu)
    mm1 = PlanNode(relops.MemCpy(), cpu)
    mm2 = PlanNode(relops.MemCpy(), gpu)
    cpu2gpu = PlanNode(relops.CPU2GPU(), gpu)
    gpu2cpu = PlanNode(relops.GPU2CPU(), gpu)

    cpu_d = {"device": cpu}
    gpu_d = {"device": gpu}
    g.add_nodes_from([cpu_op, gpu_op, router, dummy, mm1, mm2, cpu2gpu, gpu2cpu])
    g.add_edges_from(
        [(router, mm1, cpu_d), (router, mm2, gpu_d), (mm1, cpu_op, cpu_d), (cpu_op, dummy, cpu_d),
         (mm2, cpu2gpu, gpu_d),
         (cpu2gpu, gpu_op, gpu_d),
         (gpu_op, gpu2cpu, gpu_d), (gpu2cpu, dummy, gpu_d)])
    assert nx.is_directed_acyclic_graph(g)
    return g


def get_het_graph_for_join(op: relops.RelJoin) -> nx.DiGraph:
    g = nx.DiGraph()
    cpu = CPU()
    gpu = GPU()
    cpu_op = PlanNode(op, cpu)
    gpu_op = PlanNode(op, gpu)
    router_a = PlanNode(relops.Router(), cpu)
    router_b = PlanNode(relops.Router(), cpu)
    mms = [PlanNode(relops.MemCpy(), (lambda x: cpu if x % 2 else gpu)(i)) for i in range(4)]
    cpu2gpu_a = PlanNode(relops.CPU2GPU(), gpu)
    cpu2gpu_b = PlanNode(relops.CPU2GPU(), gpu)
    gpu2cpu = PlanNode(relops.GPU2CPU(), gpu)
    dummy = PlanNode(relops.Dummy(), cpu)

    g.add_nodes_from([cpu_op, gpu_op, router_a, router_b, cpu2gpu_a, cpu2gpu_b, gpu2cpu, dummy])
    g.add_nodes_from(mms)

    cpu_d = {"device": cpu}
    gpu_d = {"device": gpu}
    g.add_edges_from(
        [(router_a, mms[0], cpu_d), (router_a, mms[1], gpu_d), (mms[0], cpu_op, cpu_d), (cpu_op, dummy, cpu_d),
         (mms[1], cpu2gpu_a, gpu_d),
         (cpu2gpu_a, gpu_op, gpu_d), (gpu_op, gpu2cpu, gpu_d), (gpu2cpu, dummy, gpu_d), (router_b, mms[2], cpu_d),
         (router_b, mms[3], gpu_d),
         (mms[3], cpu2gpu_b, gpu_d), (cpu2gpu_b, gpu_op, gpu_d), (mms[2], cpu_op, cpu_d)])
    assert nx.is_directed_acyclic_graph(g)
    return g


def sources(g: nx.DiGraph):
    return [node for node, deg in g.in_degree() if deg == 0]


def drains(g: nx.DiGraph):
    return [node for node, deg in g.out_degree() if deg == 0]


def get_routers(g: nx.DiGraph):
    return [node for node in g if node.is_router()]


def connect(a: nx.DiGraph, b: nx.DiGraph) -> nx.DiGraph:
    assert (len(drains(a)) == 1)
    assert (len(sources(b)) > 0)

    dummy = drains(a)[0]
    preds = a.predecessors(dummy)
    src = sources(b)[0]
    g = nx.compose(a, b)

    for node in preds:
        g.add_edges_from([(node, src, {"device": CPU()})])
    g.remove_node(dummy)
    return g


def connect_join(a: nx.DiGraph, b: nx.DiGraph, join: nx.DiGraph) -> nx.DiGraph:
    assert (len(sources(join)) == 2)
    assert (len(drains(a)) == len(drains(b)) == 1)

    dummy_a = drains(a)[0]
    dummy_b = drains(b)[0]
    preds_a = a.predecessors(dummy_a)
    preds_b = b.predecessors(dummy_b)

    src_a = sources(join)[0]
    src_b = sources(join)[1]

    g = nx.compose(a, b)
    g = nx.compose(g, join)

    for node in preds_a:
        g.add_edges_from([(node, src_a, {"device": CPU()})])
    for node in preds_b:
        g.add_edges_from([(node, src_b, {"device": CPU()})])

    g.remove_node(dummy_a)
    g.remove_node(dummy_b)
    return g
