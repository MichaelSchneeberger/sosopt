from __future__ import annotations

from dataclasses import dataclass, replace
from functools import cached_property

from donotation import do

import statemonad
from statemonad.typing import StateMonad

from polymat.typing import PolynomialExpression, VectorExpression, State

from sosopt.constraints.constraint import Constraint
from sosopt.constraints.constraintprimitives.constraintprimitive import (
    ConstraintPrimitive,
    EqualityConstraintPrimitive,
    LinearConstraintPrimitive,
    SDPConstraintPrimitive,
)
from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol
from sosopt.solvers.solveargs import get_solver_args
from sosopt.solvers.solvermixin import SolverMixin
from sosopt.solvers.solverdata import SolutionFound, SolutionNotFound, SolverData


@dataclass(frozen=True)
class SOSResultMapping:
    solver_data: SolverData
    symbol_values: dict[DecisionVariableSymbol, tuple[float, ...]]


@dataclass(frozen=True)
class SOSProblem:
    """
    Generic sum of squares problem.
    This problem contains expression objects.
    """

    lin_cost: PolynomialExpression
    quad_cost: VectorExpression | None
    constraints: tuple[Constraint, ...]
    solver: SolverMixin
    nested_constraint_primitives: tuple[ConstraintPrimitive, ...]

    @property
    def constraint_primitives(self) -> tuple[ConstraintPrimitive, ...]:
        def gen_flattened_primitives():
            for primitive in self.nested_constraint_primitives:
                yield from primitive.flatten()

        return tuple(gen_flattened_primitives())

    def copy(self, /, **others):
        return replace(self, **others)

    @cached_property
    def decision_variable_symbols(self) -> tuple[DecisionVariableSymbol, ...]:
        def gen_decision_variable_symbols():
            for primitive in self.constraint_primitives:
                yield from primitive.decision_variable_symbols

        return tuple(sorted(set(gen_decision_variable_symbols())))

    def eval(self, substitutions: dict[DecisionVariableSymbol, tuple[float, ...]]):
        def evaluate_primitives():
            for primitive in self.nested_constraint_primitives:
                n_primitive = primitive.eval(substitutions)

                # constraint still contains decision variables
                if n_primitive is not None:
                    yield n_primitive

        primitives = tuple(evaluate_primitives())
        return self.copy(nested_constraint_primitives=primitives)

    def solve(self) -> StateMonad[State, SOSResultMapping]:
        @do()
        def solve_sdp():
            state = yield from statemonad.get[State]()

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
                (primitive.name, primitive.to_constraint_vector())
                for primitive in self.constraint_primitives
                if isinstance(primitive, SDPConstraintPrimitive)
            )

            # filter linear inequality constraints
            l_data = tuple(
                (primitive.name, primitive.to_constraint_vector())
                for primitive in self.constraint_primitives
                if isinstance(primitive, LinearConstraintPrimitive)
            )

            # filter linear equality constraints
            eq_data = tuple(
                (primitive.name, primitive.to_constraint_vector())
                for primitive in self.constraint_primitives
                if isinstance(primitive, EqualityConstraintPrimitive)
            )

            solver_args = yield from get_solver_args(
                indices=indices,
                lin_cost=self.lin_cost,
                quad_cost=self.quad_cost,
                s_data=s_data,
                q_data=None,
                l_data=l_data,
                eq_data=eq_data,
            )

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

            sos_result_mapping = SOSResultMapping(
                solver_data=solver_data,
                symbol_values=symbol_values,
            )

            return statemonad.from_(sos_result_mapping)

        return solve_sdp()


def sos_problem(
    lin_cost: PolynomialExpression,
    constraints: tuple[Constraint, ...],
    solver: SolverMixin,
    quad_cost: VectorExpression | None = None,
):
    def gen_primitives():
        for constraint in constraints:
            for primitive in constraint.get_constraint_primitives():
                yield primitive

    primitives = tuple(gen_primitives())

    return SOSProblem(
        lin_cost=lin_cost,
        quad_cost=quad_cost,
        constraints=constraints,
        solver=solver,
        nested_constraint_primitives=primitives,
    )

