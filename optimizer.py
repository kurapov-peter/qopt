from plan import Plan
import sobol
import pygad
from bees_algorithm import BeesAlgorithm


def optimize(plan: Plan, samples_num=400, candidates_for_local_search=10):
    features = plan.get_features()
    routers_coeffs = features['routers']
    samples = sobol.sample(len(routers_coeffs), n_points=samples_num)

    def generate_candidates(generator):
        for sample in generator:
            plan.set_routers_coeffs(sample)
            generate_candidates.cost_recalc_counter += 1
            yield {'sample': sample, 'cost': plan.cost()}

    generate_candidates.cost_recalc_counter = 0

    candidates = sorted(list(generate_candidates(samples)), key=lambda k: k['cost'])[:candidates_for_local_search]
    # print(candidates)

    plan.set_routers_coeffs(candidates[0]['sample'])
    print("Parameters of the best solution : {solution}".format(solution=candidates[0]['sample']))
    print('Found solution with cost: ', plan.cost(), ' after ', generate_candidates.cost_recalc_counter,
          ' cost recalculations.')
    return plan


def genetic_search(plan):
    features = plan.get_features()
    initial_pop = features['routers']

    def fitness(solution, solution_idx):
        fitness.cost_recalc_counter += 1
        plan.set_routers_coeffs(solution)
        return 1.0 / plan.cost()

    fitness.cost_recalc_counter = 0

    fitness_func = fitness
    num_generations = 50
    num_parents_mating = 4
    sol_per_pop = 8

    ga_instance = pygad.GA(num_generations=num_generations,
                           num_parents_mating=num_parents_mating,
                           fitness_func=fitness_func,
                           # initial_population=initial_pop,
                           num_genes=len(initial_pop),
                           sol_per_pop=sol_per_pop,
                           gene_type=float,
                           init_range_low=0,  # no action as init pop is present
                           init_range_high=1,
                           parent_selection_type="sss",
                           keep_parents=1,
                           mutation_type='random',
                           mutation_by_replacement=True,
                           mutation_num_genes=1,
                           random_mutation_min_val=0,
                           random_mutation_max_val=1)
    ga_instance.run()
    solution, solution_fitness, solution_idx = ga_instance.best_solution()
    print("Parameters of the best solution : {solution}".format(solution=solution))
    print("Fitness value of the best solution = {solution_fitness}".format(solution_fitness=solution_fitness))
    plan.set_routers_coeffs(solution)
    print('Found solution with cost: ', plan.cost(), ' after ', fitness.cost_recalc_counter,
          ' cost recalculations.')
    return plan


def bees_alg_opt(plan):
    routers_cnt = len(plan.get_features()['routers'])
    search_boundaries = ([0.0 for _ in range(routers_cnt)], [1.0 for _ in range(routers_cnt)])
    cost_recalc_counter = 0

    def hypersphere(solution):
        nonlocal cost_recalc_counter
        plan.set_routers_coeffs(solution)
        cost_recalc_counter += 1
        return -plan.cost()

    alg = BeesAlgorithm(hypersphere, search_boundaries[0], search_boundaries[1])
    alg.performFullOptimisation(max_iteration=5)
    best = alg.best_solution
    plan.set_routers_coeffs(best.values)
    print("Bee algorithm:")
    print("Parameters of the best solution : {solution}".format(solution=best.values))
    print('Found solution with cost: ', plan.cost(), ' after ', cost_recalc_counter,
          ' cost recalculations.')
    return plan
