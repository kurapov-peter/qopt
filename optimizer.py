from plan import Plan
import sobol


def optimize(plan: Plan, samples_num=1000, candidates_for_local_search=10):
    features = plan.get_features()
    routers_coeffs = features['routers']
    samples = sobol.sample(len(routers_coeffs), n_points=samples_num)

    def generate_candidates(generator):
        for sample in generator:
            plan.set_routers_coeffs(sample)
            yield {'sample': sample, 'cost': plan.cost()}

    candidates = sorted(list(generate_candidates(samples)), key=lambda k: k['cost'])[:candidates_for_local_search]
    # print(candidates)

    plan.set_routers_coeffs(candidates[0]['sample'])
    return plan


def genetic_search(plan):
    return plan
