from __future__ import annotations
from dataclasses import replace

from dataclassabc import dataclassabc

import statemonad

import polymat
from polymat.typing import MatrixExpression, VariableVectorExpression, State

from sosopt.polynomialconstraints.constraintprimitive.constraintprimitive import ConstraintPrimitive
from sosopt.polynomialconstraints.constraintprimitive.zeropolynomialprimitive import init_zero_polynomial_primitive
from sosopt.utils.decisionvariablesmixin import to_decision_variable_symbols
from sosopt.polynomialconstraints.polynomialconstraint import PolynomialConstraint
from sosopt.utils.polynomialvariablesmixin import PolynomialVariablesMixin, to_polynomial_variables


@dataclassabc(frozen=True, slots=True)
class ZeroPolynomialConstraint(PolynomialVariablesMixin, PolynomialConstraint):
    name: str
    primitives: tuple[ConstraintPrimitive, ...]
    polynomial_variables: VariableVectorExpression

    # the parametrized polynomial matrix that is required to be zero in each entry
    zero_matrix: MatrixExpression

    # shape of the polynomial matrix
    shape: tuple[int, int]

    def copy(self, /, **others):
        return replace(self, **others)


def init_zero_polynomial_constraint(
    name: str,
    zero_matrix: MatrixExpression,
):

    def create_constraint(state: State):
        state, polynomial_variables = to_polynomial_variables(zero_matrix).apply(state)

        state, (n_rows, n_cols) = polymat.to_shape(zero_matrix).apply(state)

        constraint_primitives = []

        for row in range(n_rows):
            for col in range(n_cols):
                condition_entry = zero_matrix[row, col]

                state, decision_variable_symbols = to_decision_variable_symbols(condition_entry).apply(state)               

                constraint_primitives.append(
                    init_zero_polynomial_primitive(
                        name=name,
                        expression=condition_entry,
                        polynomial_variables=polynomial_variables,
                        decision_variable_symbols=decision_variable_symbols,
                    )
                )

        constraint = ZeroPolynomialConstraint(
            name=name,
            zero_matrix=zero_matrix,
            shape=(n_rows, n_cols),
            polynomial_variables=polynomial_variables,
            primitives=tuple(constraint_primitives),
        )
        return state, constraint
    
    return statemonad.get_map_put(create_constraint)
