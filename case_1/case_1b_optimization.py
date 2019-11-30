#!/usr/bin/env python3

from CADETProcess.simulation import Cadet, ProcessEvaluator
from CADETProcess.optimization import OptimizationProblem
from CADETProcess.common import RankedPerformance

from case_1b_simulation import batch_binary

process_simulator = Cadet()
process_simulator.evaluate_stationarity = True

ranking = [1, 1]
purity_required = [0.95, 0.95]
evaluator = ProcessEvaluator(process_simulator, purity_required, ranking)

optimization_problem = OptimizationProblem(batch_binary, evaluator,
                                           name='case_1b', save_log=True)

def objective_function(performance):
    ranked = RankedPerformance(performance, ranking)
    return - ranked.productivity * ranked.recovery * ranked.eluent_consumption

optimization_problem.objective_fun = objective_function

optimization_problem.add_variable('cycle_time', lb=10, ub=600)
optimization_problem.add_variable('feed_duration.time', lb=10, ub=100)

optimization_problem.add_linear_constraint(
        opt_vars=['feed_duration.time', 'cycle_time'], factors=[1,-1], b=0)


if __name__ == "__main__":
    from CADETProcess.optimization import DEAP as Solver

    opt_solver = Solver()
    results = opt_solver.optimize(optimization_problem, save_results=True)
