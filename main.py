import networkx as nx
import relops
from device import Device
import graph_utils


if __name__ == '__main__':
    scan_a = graph_utils.get_het_graph_for(relops.RelScan())
    scan_b = graph_utils.get_het_graph_for(relops.RelScan())
    join = graph_utils.get_het_graph_for(relops.RelJoin())
    graph_utils.display(join)
    res = graph_utils.connect_join(scan_a, scan_b, join)
    graph_utils.display(res)
