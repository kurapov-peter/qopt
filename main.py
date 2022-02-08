import string
import sys
import plan_parser
import graph_utils
from plan import Plan
import argparse
from optimizer import optimize, genetic_search, brute_force_opt
import json


def main(args):
    data = json.load(args.plan_input)
    final = plan_parser.get_plan(data)
    graph_utils.display(final)

    p = Plan(final)

    coeffs_len = len(p.get_features()['routers'])
    p.set_routers_use_cpu_only()
    print('All cpu cost: ', p.cost())
    # p.set_routers_use_gpu_only()
    # print('All gpu cost: ', p.cost())
    # p.display()
    p.set_routers_coeffs([0.5] * coeffs_len)
    print('Half: ', p.cost())
    #
    # optimize(p)
    #
    # p.set_routers_coeffs([1 for _ in range(coeffs_len)])
    # # print(p.cost())
    #
    # genetic_search(p)
    brute_force_opt(p)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--plan_input', help='Path to input json file.', type=argparse.FileType('r'),
                        default=sys.stdin)
    args = parser.parse_args()
    main(args)
