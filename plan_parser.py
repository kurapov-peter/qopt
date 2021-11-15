import graph_utils
import relops
from data_params import DataParams


def get_relop(rel):
    relop_name = rel['relOp']
    if relop_name == 'LogicalTableScan':
        table_data = DataParams(100)
        return relops.RelScan(rel['table'][1], table_data)
    if relop_name == 'LogicalProject':
        return relops.RelProject()
    if relop_name == 'LogicalFilter':
        return relops.RelFilter()
    if relop_name == 'LogicalAggregate':
        return relops.RelAgg()
    if relop_name == 'LogicalJoin':
        return relops.RelJoin()
    if relop_name == 'LogicalSort':
        return relops.RelSort()
    if relop_name == 'LogicalUnion':
        raise NotImplementedError("Unions are not implemented.")


def get_plan(data):
    nodes = []
    rel_cnt = len(data['rels'])
    for rel in data['rels']:
        relop = get_relop(rel)
        if len(nodes) == rel_cnt - 1:
            nodes.append(graph_utils.finalize_graph_with(nodes[-1], relop))
        else:
            if rel['relOp'] == 'LogicalTableScan':
                nodes.append(graph_utils.get_het_graph_for(relop))
                continue
            if rel['relOp'] == 'LogicalJoin':
                join = graph_utils.get_het_graph_for(relop)
                inputs = list(map(int, rel['inputs']))
                nodes.append(graph_utils.connect_join(nodes[inputs[0]], nodes[inputs[1]], join))
                continue
            op = graph_utils.get_het_graph_for(relop)
            nodes.append(graph_utils.connect(nodes[-1], op))

    return nodes[-1]
