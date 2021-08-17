from plan import Plan
import sobol


def optimize(plan: Plan):
    features = plan.get_features()
    routers_coeffs = features['routers']
    samples = sobol.sample(len(routers_coeffs), n_points=10, skip=1000)
    for sample in samples:
        plan.set_routers_coeffs(sample)
        print(sample, '\tcost = ', int(plan.cost()))
    return plan
