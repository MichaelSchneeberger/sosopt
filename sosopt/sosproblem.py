from __future__ import annotations

from dataclasses import dataclass, replace

import statemonad

from polymat.typing import State, PolynomialExpression, VectorExpression

from sosopt.conicproblem import ConicProblem
from sosopt.polynomialconstraints.polynomialconstraint import PolynomialConstraint
from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol
from sosopt.solvers.solvermixin import SolverMixin


@dataclass(frozen=True)
class SOSProblem:
    """
    Generic sum of squares problem.
    This problem contains expression objects.
    """

    lin_cost: PolynomialExpression
    quad_cost: VectorExpression | None
    constraints: tuple[PolynomialConstraint, ...]
    solver: SolverMixin
    # conic_problem: ConicProblem

    def copy(self, /, **others):
        return replace(self, **others)

    def eval(self, substitutions: dict[DecisionVariableSymbol, tuple[float, ...]]):
        def gen_evaluated_constraints():
            for constraint in self.constraints:
                evaluated_constraint = constraint.eval(substitutions)

                if evaluated_constraint:
                    yield evaluated_constraint

        evaluated_constraints = tuple(gen_evaluated_constraints())
        return init_sos_problem(
            lin_cost=self.lin_cost,
            quad_cost=self.quad_cost,
            solver=self.solver,
            constraints=evaluated_constraints,
        )

    def to_conic_problem(self):
        def gen_cone_constraints():
            for constraint in self.constraints:
                for primitive in constraint.primitives:
                    yield primitive.to_cone_constraint()

        cone_constraints = tuple(gen_cone_constraints())

        problem = ConicProblem(
            lin_cost=self.lin_cost,
            quad_cost=self.quad_cost,
            solver=self.solver,
            constraints=cone_constraints,
        )

        # return statemonad.from_[State](problem)
        return problem

    def solve(self):
        return self.to_conic_problem().solve()


def init_sos_problem(
    lin_cost: PolynomialExpression,
    constraints: tuple[PolynomialConstraint, ...],
    solver: SolverMixin,
    quad_cost: VectorExpression | None = None,
):
    # match solver:
    #     case MosekSolver() if quad_cost is not None:
    #         n_lin_cost, quad_cost_constraint = yield from to_linear_cost(
    #             name='quad_to_lin_cost',
    #             lin_cost=lin_cost,
    #             quad_cost=quad_cost,
    #         )
    #         n_quad_cost = None
    #         n_constraints = constraints + (quad_cost_constraint,)

    #     case _:
    # n_lin_cost = lin_cost
    # n_quad_cost = quad_cost
    # n_constraints = constraints

    # def gen_cone_constraints():
    #     for constraint in constraints:
    #         for primitive in constraint.primitives:
    #             yield primitive.to_cone_constraint()

    # cone_constraints = tuple(gen_cone_constraints())

    # conic_problem = ConicProblem(
    #     lin_cost=lin_cost,
    #     quad_cost=quad_cost,
    #     solver=solver,
    #     constraints=cone_constraints
    # )

    return statemonad.from_(
        SOSProblem(
            lin_cost=lin_cost,
            quad_cost=quad_cost,
            constraints=constraints,
            solver=solver,
            # conic_problem=conic_problem,
        )
    )
