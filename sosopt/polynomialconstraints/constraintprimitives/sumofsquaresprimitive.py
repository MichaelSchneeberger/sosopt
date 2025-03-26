from __future__ import annotations

from dataclasses import replace
from typing import override

from dataclassabc import dataclassabc

from polymat.typing import (
    ScalarPolynomialExpression,
)

from sosopt.coneconstraints.semidefiniteconstraint import init_semi_definite_constraint
from sosopt.polymat.from_ import square_matricial_representation
from sosopt.polynomialconstraints.constraintprimitives.polynomialconstraintprimitive import (
    PolynomialConstraintPrimitive,
)
from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol
from sosopt.polynomialconstraints.polynomialvariablesmixin import PolynomialVariablesMixin


@dataclassabc(frozen=True, slots=True)
class SumOfSquaresPrimitive(PolynomialVariablesMixin, PolynomialConstraintPrimitive):
    name: str
    expression: ScalarPolynomialExpression
    polynomial_variable_indices: tuple[int, ...]
    decision_variable_symbols: tuple[DecisionVariableSymbol, ...]

    def gram_matrix(self, sparse_gram: bool):
        if sparse_gram:
            return self.expression.to_gram_matrix(
                self.polynomial_variable
            ).cache()
        else:
            return square_matricial_representation(
                expression=self.expression,
                variables=self.polynomial_variable,
            ).cache()

    def copy(self, /, **others):
        return replace(self, **others)
    
    @override
    def to_cone_constraint(self, settings: dict):
        return init_semi_definite_constraint(
            name=self.name,
            expression=self.gram_matrix(settings['sparse_gram']),
            decision_variable_symbols=self.decision_variable_symbols,
        )


def init_sum_of_squares_primitive(
    name: str,
    expression: ScalarPolynomialExpression,
    polynomial_variable_indices: tuple[int, ...],
    decision_variable_symbols: tuple[DecisionVariableSymbol, ...],
):
    return SumOfSquaresPrimitive(
        name=name,
        expression=expression,
        polynomial_variable_indices=polynomial_variable_indices,
        decision_variable_symbols=decision_variable_symbols,
    )
