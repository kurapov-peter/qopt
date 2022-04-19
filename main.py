import argparse
import json
import sys
from enum import Enum

import graph_utils
import plan_parser
from optimizer import brute_force_opt, firefly, genetic_search, optimize
from plan import Plan


class OptimizationAlgorithm(Enum):
    bruteforce = 'bruteforce'
    genetic = 'genetic'
    firefly = 'firefly'
    default = 'default'

    def __str__(self) -> str:
        return self.value

def run_optimization(algorithm, plan):
    match algorithm:
        case OptimizationAlgorithm.bruteforce:
            return brute_force_opt(plan)
        case OptimizationAlgorithm.genetic:
            return genetic_search(plan)
        case OptimizationAlgorithm.firefly:
            return firefly(plan)
        case OptimizationAlgorithm.default:
            return optimize(plan)
        case _:
            raise AttributeError('Invalid algorithm.')

def main(args):
    data = json.load(args.plan_input)
    final = plan_parser.get_plan(data)

    if args.display:
        graph_utils.display(final)

    p = Plan(final)
    p.set_routers_use_cpu_only()
    print('All cpu cost: ', p.cost())
    
    run_optimization(args.algorithm, p)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--plan_input', help='Path to input json file.', type=argparse.FileType('r'),
                        default=sys.stdin)
    parser.add_argument('-a', "--algorithm", type=OptimizationAlgorithm, choices=list(OptimizationAlgorithm), help='Optimization algorithm to use')
    parser.add_argument("--display", action='store_true')
    args = parser.parse_args()
    main(args)
