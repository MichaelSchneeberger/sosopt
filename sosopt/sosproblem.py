from __future__ import annotations

from dataclasses import dataclass, replace
from functools import cached_property

from polymat.typing import PolynomialExpression, VectorExpression

from sosopt.coneproblem import ConeProblem, init_sdp_problem
from sosopt.sosconstraints.constraint import Constraint
from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol
from sosopt.solvers.solvermixin import SolverMixin



@dataclass(frozen=True)
class SOSProblem:
    """
    Generic sum of squares problem.
    This problem contains expression objects.
    """

    constraints: tuple[Constraint, ...]
    sdp_problem: ConeProblem

    @property
    def lin_cost(self):
        return self.sdp_problem.lin_cost

    @property
    def quad_cost(self):
        return self.sdp_problem.quad_cost

    @property
    def cone_constraints(self):
        return self.sdp_problem.flattened_constraints

    def copy(self, /, **others):
        return replace(self, **others)

    @cached_property
    def decision_variable_symbols(self):
        return self.sdp_problem.decision_variable_symbols

    def eval(self, substitutions: dict[DecisionVariableSymbol, tuple[float, ...]]):
        return self.sdp_problem.eval(substitutions=substitutions)

    def solve(self):
        return self.sdp_problem.solve()


def init_sos_problem(
    lin_cost: PolynomialExpression,
    constraints: tuple[Constraint, ...],
    solver: SolverMixin,
    quad_cost: VectorExpression | None = None,
):
    def gen_cone_constraints():
        for constraint in constraints:
            yield from constraint.get_cone_constraints()

    cone_constraints = tuple(gen_cone_constraints())

    sdp_problem = init_sdp_problem(
        lin_cost=lin_cost,
        quad_cost=quad_cost,
        constraints=cone_constraints,
        solver=solver,
    )

    return SOSProblem(
        constraints=constraints,
        sdp_problem=sdp_problem,
    )

