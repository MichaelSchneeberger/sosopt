import picos as pc

from sosopt.solvers.solveargs import SolverArgs
from sosopt.solvers.solvermixin import SolverMixin


class PICOSSolver(SolverMixin):
    def solve(self, info: SolverArgs):
        x = pc.RealVariable('x', info.lin_cost.n_param)

        p = pc.Problem()

        p.minimize = info.lin_cost[1] * x

        for array in info.s_data:
            array[0] + array[1] * x

            p +=