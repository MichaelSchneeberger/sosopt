from abc import abstractmethod
from sosopt.solvers.solveargs import SolverArgs
from sosopt.solvers.solverdata import SolverData


class SolverMixin:
    @abstractmethod
    def solve(self, info: SolverArgs) -> SolverData: ...
