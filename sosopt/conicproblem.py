from __future__ import annotations

from dataclasses import dataclass, replace
from functools import cached_property

import statemonad

from polymat.typing import ScalarPolynomialExpression, VectorExpression, State

from sosopt.conversions import to_linear_cost
from sosopt.coneconstraints.coneconstraint import ConeConstraint
from sosopt.coneconstraints.equalityconstraint import EqualityConstraint
from sosopt.coneconstraints.semidefiniteconstraint import SemiDefiniteConstraint
from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol
from sosopt.solvers.solveargs import SolverArgs, to_solver_args
from sosopt.solvers.solvermixin import SolverMixin
from sosopt.solvers.solverdata import SolutionFound, SolutionNotFound, SolverData


@dataclass(frozen=True)
class ConicProblemResult:
    solver_data: SolverData
    symbol_values: dict[DecisionVariableSymbol, tuple[float, ...]]


@dataclass(frozen=True)
class ConicProblem:
    lin_cost: ScalarPolynomialExpression
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
    
    def to_linear_cost(self):
        match self.quad_cost:
            case None:
                return statemonad.from_[State](self)
            case _:
                def create_conic_problem(args):
                    t, constr = args

                    return init_conic_problem(
                        lin_cost=t,
                        constraints=self.constraints + (constr,),
                        solver=self.solver,
                    )

                return (
                    to_linear_cost(name='quad_to_lin_cost', lin_cost=self.lin_cost, quad_cost=self.quad_cost)
                    .map(create_conic_problem)
                )

    def _to_variable_index_ranges(self, state: State):
        def gen_variable_index_ranges():
            for variable in self.decision_variable_symbols:
                # raises an exception if variable doesn't exist
                index_range = state.get_index_range(variable)
                yield variable, index_range

        return dict(gen_variable_index_ranges())

    def to_solver_args(self):
        def to_solver_args_with_state(state: State):
            variable_index_ranges = self._to_variable_index_ranges(state)

            indices = tuple(
                index for start, stop in variable_index_ranges.values() for index in range(start, stop)
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

            return to_solver_args(
                indices=indices,
                lin_cost=self.lin_cost,
                quad_cost=self.quad_cost,
                s_data=s_data,
                q_data=None,    # not yet implemented
                l_data=None,    # not yet implemented
                eq_data=eq_data,
            ).apply(state)
        
        return statemonad.get_map_put(to_solver_args_with_state)

    def solve(self, solver_args: SolverArgs | None = None):
        def solve_and_retrieve_symbol_values(
                solver_args: SolverArgs,
                variable_index_ranges: dict[DecisionVariableSymbol, tuple[int, int]]
        ):
            solver_data = self.solver.solve(solver_args)

            match solver_data:
                case SolutionNotFound():
                    symbol_values = {}

                case SolutionFound():
                    solution = solver_data.solution

                    def gen_symbol_values():
                        for symbol, (start, stop) in variable_index_ranges.items():

                            solution_sel = [solver_args.indices.index(index) for index in range(start, stop)]

                            yield (
                                symbol,
                                # convert numpy.float to float
                                tuple(float(v) for v in solution[solution_sel]),
                            )

                    symbol_values = dict(gen_symbol_values())

                case _:
                    raise Exception(f'Unknown return value from solver {self.solver}.')

            return ConicProblemResult(
                solver_data=solver_data,
                symbol_values=symbol_values,
            )

        def solve_with_state(state: State, solver_args=solver_args):
            variable_index_ranges = self._to_variable_index_ranges(state)

            if solver_args is None:
                state, solver_args = self.to_solver_args().apply(state)

            sos_result_mapping = solve_and_retrieve_symbol_values(
                solver_args=solver_args,
                variable_index_ranges=variable_index_ranges,
            )

            return state, sos_result_mapping

        return statemonad.get_map_put(solve_with_state)


def init_conic_problem(
    lin_cost: ScalarPolynomialExpression,
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
