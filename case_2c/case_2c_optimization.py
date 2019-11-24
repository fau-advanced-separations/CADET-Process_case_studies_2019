#!/usr/bin/env python3

from CADETProcess.simulation import Cadet, ProcessEvaluator
from CADETProcess.optimization import OptimizationProblem
from CADETProcess.common import RankedPerformance

from case_2c_simulation import batch_long_ternary

process_simulator = Cadet()
process_simulator.evaluate_stationarity = True

ranking = [0, 1, 0]
purity_required = [0, 0.95, 0]
evaluator = ProcessEvaluator(process_simulator, purity_required, ranking)

optimization_problem = OptimizationProblem(batch_long_ternary, evaluator,
                                           name='case_2c', save_log=True)

def objective_function(performance):
    ranked = RankedPerformance(performance, ranking)
    return - ranked.productivity * ranked.recovery * ranked.eluent_consumption

optimization_problem.objective_fun = objective_function

optimization_problem.add_variable('cycle_time', lb=10, ub=600)
optimization_problem.add_variable('feed_duration.time', lb=10, ub=100)
optimization_problem.add_variable('flow_sheet.column.length', lb=0.1, ub=1.2)

optimization_problem.add_linear_constraint(
        opt_vars=['feed_duration.time', 'cycle_time'], factors=[1,-1], b=0)


if __name__ == "__main__":
    from CADETProcess.optimization import DEAP as Solver

    opt_solver = Solver()
    results = opt_solver.optimize(optimization_problem, save_results=True)
