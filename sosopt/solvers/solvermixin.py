from abc import abstractmethod
from typing import NamedTuple

from polymat.typing import ArrayRepr
from sosopt.solvers.solverdata import SolverData


class SolveArgs(NamedTuple):
    lin_cost: ArrayRepr
    quad_cost: ArrayRepr | None
    l_data: tuple[ArrayRepr, ...]
    q_data: tuple[ArrayRepr, ...]
    s_data: tuple[ArrayRepr, ...]


class SolverMixin:
    @abstractmethod
    def solve(self, info: SolveArgs) -> SolverData: ...
