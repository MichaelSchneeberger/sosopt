from __future__ import annotations

from dataclasses import dataclass, replace
from functools import cached_property

from donotation import do

from polymat.typing import PolynomialExpression, VectorExpression

from sosopt.conicproblem import ConicProblem
from sosopt.conversions import to_linear_cost
from sosopt.polynomialconstraints.polynomialconstraint import PolynomialConstraint
from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol
from sosopt.solvers.cvxoptsolver import CVXOPTSolver
from sosopt.solvers.moseksolver import MosekSolver
from sosopt.solvers.solvermixin import SolverMixin
import statemonad


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

    def copy(self, /, **others):
        return replace(self, **others)

    # @cached_property
    # def decision_variable_symbols(self) -> tuple[DecisionVariableSymbol, ...]:
    #     def gen_decision_variable_symbols():
    #         for constraint in self.constraints:
    #             for primitive in constraint.primitives:
    #                 yield from primitive.decision_variable_symbols

    #     return tuple(sorted(set(gen_decision_variable_symbols())))

    def eval(self, substitutions: dict[DecisionVariableSymbol, tuple[float, ...]]):
        def gen_evaluated_constraints():
            for constraint in self.constraints:
                evaluated_constraint = constraint.eval(substitutions)

                if evaluated_constraint:
                    yield evaluated_constraint

        evaluated_constraints = tuple(gen_evaluated_constraints())
        return self.copy(constraints=evaluated_constraints)

    def get_cone_problem(self):
        def gen_cone_constraints():
            for constraint in self.constraints:
                for primitive in constraint.primitives:
                    yield primitive.to_cone_constraint()

        cone_constraints = tuple(gen_cone_constraints())
            
        problem = ConicProblem(
            lin_cost=self.lin_cost,
            quad_cost=self.quad_cost,
            solver=self.solver,
            constraints=cone_constraints
        )

        return problem

    def solve(self):
        return self.get_cone_problem().solve()


@do()
def init_sos_problem(
    lin_cost: PolynomialExpression,
    constraints: tuple[PolynomialConstraint, ...],
    solver: SolverMixin,
    quad_cost: VectorExpression | None = None,
):
    
    match solver:
        case MosekSolver() if quad_cost is not None:
            n_lin_cost, quad_cost_constraint = yield from to_linear_cost(
                name='quad_to_lin_cost',
                lin_cost=lin_cost,
                quad_cost=quad_cost,
            )
            n_quad_cost = None
            n_constraints = constraints + (quad_cost_constraint,)

        case _:
            n_lin_cost = lin_cost
            n_quad_cost = quad_cost
            n_constraints = constraints

    return statemonad.from_(SOSProblem(
        lin_cost=n_lin_cost,
        quad_cost=n_quad_cost,
        constraints=n_constraints,
        solver=solver,
    ))
