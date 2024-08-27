from __future__ import annotations

from polymat.typing import PolynomialExpression, VectorExpression

from sosopt.solvers.cvxoptsolver import CVXOPTSolver
from sosopt.solvers.moseksolver import MosekSolver
from sosopt.utils.grammatrix import to_gram_matrix as _to_gram_matrix
from sosopt.constraints.constraint import Constraint
from sosopt.constraints.putinarpsatzconstraint import (
    define_multiplier as _define_multiplier,
)
from sosopt.solvers.solvermixin import SolverMixin
from sosopt.polymat.from_ import define_variable as _define_variable
from sosopt.polymat.init import (
    init_polynomial_variable as _init_polynomial_variable,
)
from sosopt.problem import SOSProblem
from sosopt.semialgebraicset import SemialgebraicSet
from sosopt.constraints.init import (
    to_positive_polynomial_constraint,
    to_putinar_psatz_constraint,
)

cvx_opt_solver = CVXOPTSolver()
mosek_solver = MosekSolver()

define_variable = _define_variable
define_multiplier = _define_multiplier
define_polynomial = _init_polynomial_variable

to_gram_matrix = _to_gram_matrix

def sos_constraint(
    name: str,
    greater_than_zero: PolynomialExpression | None = None,
    less_than_zero: PolynomialExpression | None = None,
):
    if greater_than_zero is not None:
        condition = greater_than_zero
    elif less_than_zero is not None:
        condition = -less_than_zero
    else:
        raise Exception("SOS constraint requires condition.")

    return to_positive_polynomial_constraint(
        name=name,
        condition=condition,
    )


def sos_constraint_putinar(
    name: str,
    domain: SemialgebraicSet,
    greater_than_zero: PolynomialExpression | None = None,
    less_than_zero: PolynomialExpression | None = None,
):
    if greater_than_zero is not None:
        condition = greater_than_zero
    elif less_than_zero is not None:
        condition = -less_than_zero
    else:
        raise Exception("SOS constraint requires condition.")

    return to_putinar_psatz_constraint(
        name,
        condition=condition,
        domain=domain,
    )


def set_(
    equal_zero: dict[str, VectorExpression] = {},
    greater_than_zero: dict[str, VectorExpression] = {},
    less_than_zero: dict[str, VectorExpression] = {},
):
    inequalities = greater_than_zero | {n: -p for n, p in less_than_zero.items()}

    return SemialgebraicSet(
        inequalities=inequalities,
        equalities=equal_zero,
    )


def sos_problem(
    lin_cost: PolynomialExpression,
    constraints: tuple[Constraint, ...],
    solver: SolverMixin,
    quad_cost: VectorExpression | None = None,
):
    def gen_primitives():
        for constraint in constraints:
            for primitive in constraint.constraint_primitives:
                yield primitive

    primitives = tuple(gen_primitives())

    return SOSProblem(
        lin_cost=lin_cost,
        quad_cost=quad_cost,
        constraints=constraints,
        solver=solver,
        nested_constraint_primitives=primitives,
    )
