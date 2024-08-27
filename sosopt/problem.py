from __future__ import annotations

from dataclasses import dataclass, replace
from functools import cached_property

from donotation import do

import statemonad
from statemonad.typing import StateMonad

import polymat
from polymat.typing import PolynomialExpression, VectorExpression, State, Symbol

from sosopt.constraints.constraint import Constraint
from sosopt.constraints.constraintprimitives.constraintprimitive import (
    ConstraintPrimitive,
)
from sosopt.constraints.constraintprimitives.positivepolynomialconstraintprimitive import (
    PositivePolynomialConstraintPrimitive,
)
from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol
from sosopt.solvers.solvermixin import SolveArgs, SolverMixin
from sosopt.solvers.solverdata import SolverData


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
            indices = tuple(i for _, index_range in variable_index_ranges for i in index_range)

            # vector_sympy = yield from polymat.to_sympy(self.decision_variable_vector)
            # print(f'{vector_sympy}')

            lin_cost = yield from polymat.to_array(
                self.lin_cost, indices
            )

            if self.quad_cost is None:
                quad_cost = None
            else:
                quad_cost = yield from polymat.to_array(
                    self.quad_cost, indices
                )

            s_data = yield from statemonad.zip(
                (
                    primitive.to_array(indices)
                    for primitive in self.constraint_primitives
                    if isinstance(primitive, PositivePolynomialConstraintPrimitive)
                )
            )

            l_data = tuple()
            q_data = tuple()

            # maximum degree of cost function must be 2
            assert lin_cost.degree <= 1, f"{lin_cost.degree=}"

            if quad_cost is not None:
                # maximum degree of cost function must be 2
                assert quad_cost.degree <= 1, f"{quad_cost.degree=}"

            # maximum degree of constraint must be 1
            for array in l_data + q_data + s_data:
                if 1 < array.degree:                   
                    raise AssertionError(
                        (
                            "The degree of the polynomial in the decision variables used to encode the optimization problem constraints "
                            "must not exceed 1."
                        )
                    )

            solver_data = self.solver.solve(
                SolveArgs(
                    lin_cost=lin_cost,
                    quad_cost=quad_cost,
                    l_data=l_data,
                    q_data=q_data,
                    s_data=s_data,
                )
            )
            solution = solver_data.solution

            def gen_symbol_values():
                for variable, index_range in variable_index_ranges:

                    def gen_value_indices():
                        for index in index_range:
                            yield indices.index(index)

                    # convert numpy.float to float
                    yield variable, tuple(float(v) for v in solution[list(gen_value_indices())])

            symbol_values = dict(gen_symbol_values())

            sos_result_mapping = SOSResultMapping(
                solver_data=solver_data, 
                symbol_values=symbol_values,
            )

            return statemonad.from_(sos_result_mapping)

        return solve_sdp()
