import networkx as nx
import relops
from device import Device
import graph_utils


if __name__ == '__main__':
    g = graph_utils.get_het_graph_for(relops.RelScan())
    graph_utils.display(g)
    g1 = graph_utils.get_het_graph_for_join(relops.RelJoin())
    graph_utils.display(g1)
