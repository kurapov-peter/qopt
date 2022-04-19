from plan import Plan
import sobol
import pygad
import numpy as np
from  sobol_seq import i4_sobol_generate
from numpy.random import default_rng

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


def brute_force_opt(plan):
    routers_cnt = len(plan.get_features()['routers'])
    solution = [1.0 for _ in range(routers_cnt)]
    best_solution = solution.copy()
    plan.set_routers_coeffs(solution)
    min_plan_cost = plan.cost()
    cost_recalc_counter = 1

    def brute_force(ind, len):
        nonlocal plan, min_plan_cost, solution, cost_recalc_counter, best_solution
        if ind == len:
            plan.set_routers_coeffs(solution)
            plan_cost = plan.cost()
            cost_recalc_counter += 1
            if plan_cost < min_plan_cost:
                min_plan_cost = plan_cost
                best_solution = solution.copy()
            return
        for x in np.arange(0, 1.1, 0.1):
            solution[ind] = x
            brute_force(ind + 1, len)

    brute_force(0, routers_cnt)
    plan.set_routers_coeffs(best_solution)
    print("Brute force:")
    print("Parameters of the best solution : {solution}".format(solution=best_solution))
    print('Found solution with cost: ', plan.cost(), ' after ', cost_recalc_counter,
          ' cost recalculations.')
    return plan


def firefly_optimize(plan, samples = 400, local = 5, evals=35, pop=10):
    features = plan.get_features()
    routers_coeffs = features['routers']
    grid = i4_sobol_generate(len(routers_coeffs), samples)
    def generate_candidates(generator):
        for sample in generator:
            plan.set_routers_coeffs(sample)
            generate_candidates.cost_recalc_counter += 1
            yield {'sample': sample, 'cost': plan.cost()}
    generate_candidates.cost_recalc_counter = 0

    candidates = sorted(list(generate_candidates(grid)), key=lambda k: k['cost'])[:local]
    best = candidates[0]['sample']
    def my_cost(P, X):
        P.set_routers_coeffs(X)
        return P.cost()
    for candidate in candidates:
        plan.set_routers_coeffs(candidate['sample'])
        tmp = firefly(plan, n_ff=pop, eval=evals, is_local=True).get_features()['routers']
        if my_cost(plan, tmp)< my_cost(plan, best):
            best = tmp
    plan.set_routers_coeffs(best)
    return plan



def FireflyAlgorithm(function, x0, dim, lb, ub, max_evals, ff_gen, pop_size=20, alpha=0.05, betamin=1, gamma=0.05, seed=None):
    rng = default_rng()
    fireflies = ff_gen(lb, ub, pop_size, dim, x0)
    intensity = np.apply_along_axis(function, 1, fireflies)
    best = x0
    evaluations = pop_size
    new_alpha = alpha
    search_range = ub - lb

    while evaluations <= max_evals:
        new_alpha *= 0.97
        for i in range(pop_size):
            for j in range(pop_size):
                if intensity[i] >= intensity[j]:
                    r = np.sum(np.square(fireflies[i] - fireflies[j]), axis=-1)
                    beta = betamin * np.exp(-gamma * r)
                    steps = new_alpha * (rng.random(dim) - 0.5) * search_range
                    fireflies[i] += beta * (fireflies[j] - fireflies[i]) + steps
                    fireflies[i] = np.clip(fireflies[i], lb, ub)
                    intensity[i] = function(fireflies[i])
                    evaluations += 1
                    best_value = function(best)
                    if intensity[i] < best_value:
                        best = fireflies[i]
    return best


def firefly(plan, n_ff = 50, eval = 300, is_local=False):
    features = plan.get_features()
    routs = features['routers']
    local_plan  = plan
    def my_cost(X):
        local_plan.set_routers_coeffs(X)
        return local_plan.cost()

    def generateFirefliesGlobal(lb, ub, pop_size, dim, x0):
        rng = default_rng()
        res = rng.uniform(lb, ub, (pop_size, dim))
        return res

    def generateFirefliesLocal(lb, ub, pop_size, dim, x0):
        rng = default_rng()
        res = np.arange(0, pop_size * dim, dtype='float64').reshape(pop_size, dim)
        for i in range(pop_size):
            res[i] = np.clip(rng.normal(x0, 0.15, dim), lb, ub)
        return res
    gen = None
    if is_local:
        gen = generateFirefliesLocal
    else:
        gen = generateFirefliesGlobal
    min = np.full(len(routs), 0.0, dtype=np.float)
    max = np.full(len(routs), 1.0, dtype=np.float)
    best = FireflyAlgorithm(function=my_cost, dim=len(routs), lb=min,   \
                            ub=max, max_evals=eval, pop_size = n_ff, x0=routs, ff_gen=gen)
    plan.set_routers_coeffs(best)
    return plan
