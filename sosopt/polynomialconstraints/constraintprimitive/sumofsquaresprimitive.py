from __future__ import annotations

from dataclasses import replace
from typing import override

from dataclassabc import dataclassabc

from polymat.typing import (
    ScalarPolynomialExpression,
    VariableVectorExpression,
)

from sosopt.coneconstraints.semidefiniteconstraint import init_semi_definite_constraint
# from sosopt.polymat.from_ import quadratic_coefficients
from sosopt.polynomialconstraints.constraintprimitive.constraintprimitive import (
    ConstraintPrimitive,
)
from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol
from sosopt.utils.polynomialvariablesmixin import PolynomialVariablesMixin


@dataclassabc(frozen=True, slots=True)
class SumOfSquaresPrimitive(PolynomialVariablesMixin, ConstraintPrimitive):
    name: str
    expression: ScalarPolynomialExpression
    polynomial_variables: VariableVectorExpression
    decision_variable_symbols: tuple[DecisionVariableSymbol, ...]

    @property
    def gram_matrix(self):
        # return quadratic_coefficients(
        #     expression=self.expression,
        #     variables=self.polynomial_variables,
        # )
        return self.expression.to_gram_matrix(self.polynomial_variables)

    def copy(self, /, **others):
        return replace(self, **others)
    
    @override
    def to_cone_constraint(self):
        return init_semi_definite_constraint(
            name=self.name,
            expression=self.gram_matrix,
            decision_variable_symbols=self.decision_variable_symbols,
        )


def init_sum_of_squares_primitive(
    name: str,
    expression: ScalarPolynomialExpression,
    polynomial_variables: VariableVectorExpression,
    decision_variable_symbols: tuple[DecisionVariableSymbol, ...],
):
    return SumOfSquaresPrimitive(
        name=name,
        expression=expression,
        polynomial_variables=polynomial_variables,
        decision_variable_symbols=decision_variable_symbols,
    )
