#!/usr/bin/env python3

from CADETProcess.simulation import Cadet, ProcessEvaluator
from CADETProcess.optimization import OptimizationProblem
from CADETProcess.common import RankedPerformance

from case_3b_simulation import ssr_binary

process_simulator = Cadet()
process_simulator.evaluate_stationarity = True

ranking = [1, 1]
purity_required = [0.95, 0.95]
evaluator = ProcessEvaluator(process_simulator, purity_required, ranking)

optimization_problem = OptimizationProblem(ssr_binary, evaluator,
                                           name='case_3b', save_log=True)
productivity_batch = 0.02193975356603516
recovery_batch = 0.7388888917708063
eluent_consumption_batch = 2.356279655342963
def objective_function(performance):
    ranked = RankedPerformance(performance, ranking)
    return - (ranked.productivity/productivity_batch + ranked.recovery/recovery_batch + ranked.eluent_consumption/eluent_consumption_batch)

optimization_problem.objective_fun = objective_function

t0 = 190 # Dead time of column, determined from Q
optimization_problem.add_variable('cycle_time', lb=10, ub=600)
optimization_problem.add_variable('feed_duration.time', lb=10, ub=100)
optimization_problem.add_variable('recycle_on.time', lb=t0, ub=600)
optimization_problem.add_variable('recycle_off.time', lb=t0, ub=600)

optimization_problem.add_linear_constraint(
        opt_vars=['recycle_off.time', 'recycle_on.time', 'feed_duration.time',\
                  'cycle_time'], factors=[1,-1, 1, -1], b=0)
optimization_problem.add_linear_constraint(
        opt_vars=['recycle_on.time', 'recycle_off.time'], factors=[1,-1], b=0)
optimization_problem.add_linear_constraint(
        opt_vars=['recycle_off.time', 'cycle_time'], factors=[1,-2], b=0)

if __name__ == "__main__":
    from CADETProcess.optimization import DEAP as Solver

    opt_solver = Solver()
    results = opt_solver.optimize(optimization_problem, save_results=True)
