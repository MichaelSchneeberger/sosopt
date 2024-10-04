from __future__ import annotations
from dataclasses import replace

from dataclassabc import dataclassabc

import statemonad

import polymat
from polymat.typing import MatrixExpression, VariableVectorExpression, State

from sosopt.polynomialconstraints.constraintprimitive.sumofsquaresprimitive import init_sum_of_squares_primitive
from sosopt.polynomialconstraints.polynomialconstraint import PolynomialConstraint
from sosopt.polynomialconstraints.constraintprimitive.constraintprimitive import (
    ConstraintPrimitive,
)
from sosopt.utils.decisionvariablesmixin import to_decision_variable_symbols
from sosopt.utils.polynomialvariablesmixin import PolynomialVariablesMixin, to_polynomial_variables


@dataclassabc(frozen=True, slots=True)
class SumOfSqauresConstraint(PolynomialVariablesMixin, PolynomialConstraint):
    name: str
    condition: MatrixExpression
    shape: tuple[int, int]
    polynomial_variables: VariableVectorExpression
    primitives: tuple[ConstraintPrimitive, ...]

    def copy(self, /, **others):
        return replace(self, **others)


def init_sum_of_squares_constraint(
    name: str,
    condition: MatrixExpression,
):

    def create_constraint(state: State):
        state, polynomial_variables = to_polynomial_variables(condition).apply(state)

        state, (n_rows, n_cols) = polymat.to_shape(condition).apply(state)

        constraint_primitives = []

        for row in range(n_rows):
            for col in range(n_cols):
                condition_entry = condition[row, col]

                state, decision_variable_symbols = to_decision_variable_symbols(condition_entry).apply(state)               

                constraint_primitives.append(
                    init_sum_of_squares_primitive(
                        name=name,
                        expression=condition_entry,
                        decision_variable_symbols=decision_variable_symbols,
                        polynomial_variables=polynomial_variables,
                    )
                )

        constraint = SumOfSqauresConstraint(
            name=name,
            condition=condition,
            shape=(n_rows, n_cols),
            polynomial_variables=polynomial_variables,
            primitives=tuple(constraint_primitives),
        )
        return state, constraint
    
    return statemonad.get_map_put(create_constraint)
