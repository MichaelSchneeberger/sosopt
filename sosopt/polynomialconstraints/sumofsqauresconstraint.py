from __future__ import annotations
from dataclasses import replace

from dataclassabc import dataclassabc

from sosopt.state.state import State
import statemonad

import polymat
from polymat.typing import MatrixExpression

from sosopt.polynomialconstraints.constraintprimitives.decisionvariablesmixin import to_decision_variable_symbols
from sosopt.polynomialconstraints.constraintprimitives.sumofsquaresprimitive import (
    init_sum_of_squares_primitive,
)
from sosopt.polynomialconstraints.constraintprimitives.polynomialconstraintprimitive import (
    PolynomialConstraintPrimitive,
)
from sosopt.polynomialconstraints.polynomialconstraint import PolynomialConstraint
from sosopt.polynomialconstraints.polynomialvariablesmixin import (
    PolynomialVariablesMixin,
    to_polynomial_variable_indices,
)


@dataclassabc(frozen=True, slots=True)
class SumOfSqauresConstraint(PolynomialVariablesMixin, PolynomialConstraint):
    name: str  # override
    primitives: tuple[PolynomialConstraintPrimitive, ...]  # override
    polynomial_variable_indices: tuple[int, ...]  # override

    # the parametrized polynomial matrix that is required to be SOS in each entry
    positive_matrix: MatrixExpression

    # shape of polynomial matrix
    shape: tuple[int, int]

    def copy(self, /, **others):
        return replace(self, **others)


def init_sum_of_squares_constraint(
    name: str,
    positive_matrix: MatrixExpression,
):
    def create_constraint(state: State):
        state, polynomial_indices= to_polynomial_variable_indices(
            positive_matrix,
        ).apply(state)

        state, (n_rows, n_cols) = polymat.to_shape(positive_matrix).apply(state)

        constraint_primitives = []

        for row in range(n_rows):
            for col in range(n_cols):
                condition_entry = positive_matrix[row, col]

                state, decision_variable_symbols = to_decision_variable_symbols(condition_entry).apply(state)

                constraint_primitives.append(
                    init_sum_of_squares_primitive(
                        name=name,
                        expression=condition_entry,
                        decision_variable_symbols=decision_variable_symbols,
                        polynomial_variable_indices=polynomial_indices,
                        sparse_smr=state.sparse_smr,
                    )
                )

        constraint = SumOfSqauresConstraint(
            name=name,
            primitives=tuple(constraint_primitives),
            polynomial_variable_indices=polynomial_indices,
            positive_matrix=positive_matrix,
            shape=(n_rows, n_cols),
        )
        return state, constraint

    return statemonad.get_map_put(create_constraint)
