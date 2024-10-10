from __future__ import annotations

from dataclasses import dataclass, replace
from functools import cached_property

import statemonad

from polymat.typing import PolynomialExpression, VectorExpression, State

from sosopt.coneconstraints.coneconstraint import ConeConstraint
from sosopt.coneconstraints.equalityconstraint import EqualityConstraint
from sosopt.coneconstraints.semidefiniteconstraint import SemiDefiniteConstraint
from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol
from sosopt.solvers.solveargs import get_solver_args
from sosopt.solvers.solvermixin import SolverMixin
from sosopt.solvers.solverdata import SolutionFound, SolutionNotFound, SolverData


@dataclass(frozen=True)
class ConicProblemResult:
    solver_data: SolverData
    symbol_values: dict[DecisionVariableSymbol, tuple[float, ...]]


@dataclass(frozen=True)
class ConicProblem:
    lin_cost: PolynomialExpression
    quad_cost: VectorExpression | None
    constraints: tuple[ConeConstraint, ...]
    solver: SolverMixin

    def copy(self, /, **others):
        return replace(self, **others)

    @cached_property
    def decision_variable_symbols(self) -> tuple[DecisionVariableSymbol, ...]:
        def gen_decision_variable_symbols():
            for constraint in self.constraints:
                yield from constraint.decision_variable_symbols

        return tuple(sorted(set(gen_decision_variable_symbols())))

    def solve(self):
        def _solve(state: State):
            
            def gen_variable_index_ranges():
                for variable in self.decision_variable_symbols:
                    # raises exception if variable doesn't exist
                    index_range = state.get_index_range(variable)
                    yield variable, index_range

            variable_index_ranges = tuple(gen_variable_index_ranges())
            indices = tuple(
                i for _, index_range in variable_index_ranges for i in index_range
            )

            # filter positive semidefinite constraints
            s_data = tuple(
                (constraint.name, constraint.to_vector())
                for constraint in self.constraints
                if isinstance(constraint, SemiDefiniteConstraint)
            )

            # # filter linear inequality constraints
            # l_data = tuple(
            #     (constraint.name, constraint.to_vector())
            #     for constraint in self.constraints
            #     if isinstance(constraint, LinearConstraint)
            # )

            # filter linear equality constraints
            eq_data = tuple(
                (constraint.name, constraint.to_vector())
                for constraint in self.constraints
                if isinstance(constraint, EqualityConstraint)
            )

            state, solver_args = get_solver_args(
                indices=indices,
                lin_cost=self.lin_cost,
                quad_cost=self.quad_cost,
                s_data=s_data,
                q_data=None,
                l_data=None,
                eq_data=eq_data,
            ).apply(state)

            solver_data = self.solver.solve(solver_args)

            match solver_data:
                case SolutionNotFound():
                    symbol_values = {}

                case SolutionFound():
                    solution = solver_data.solution

                    def gen_symbol_values():
                        for symbol, index_range in variable_index_ranges:

                            solution_sel = [indices.index(index) for index in index_range]

                            # convert numpy.float to float
                            yield (
                                symbol,
                                tuple(float(v) for v in solution[solution_sel]),
                            )

                    symbol_values = dict(gen_symbol_values())

                case _:
                    raise Exception(f'Unknown return value from solver {self.solver}.')

            sos_result_mapping = ConicProblemResult(
                solver_data=solver_data,
                symbol_values=symbol_values,
            )

            return state, sos_result_mapping

        return statemonad.get_map_put(_solve)


def init_sdp_problem(
    lin_cost: PolynomialExpression,
    constraints: tuple[ConeConstraint, ...],
    solver: SolverMixin,
    quad_cost: VectorExpression | None = None,
):

    return ConicProblem(
        lin_cost=lin_cost,
        quad_cost=quad_cost,
        constraints=constraints,
        solver=solver,
    )
