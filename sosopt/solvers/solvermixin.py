from abc import abstractmethod
from sosopt.solvers.solveargs import SolveArgs
from sosopt.solvers.solverdata import SolverData


class SolverMixin:
    @abstractmethod
    def solve(self, info: SolveArgs) -> SolverData: ...
