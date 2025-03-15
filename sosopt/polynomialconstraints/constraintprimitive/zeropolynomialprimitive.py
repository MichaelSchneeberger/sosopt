from __future__ import annotations

from dataclasses import replace
from typing import override

from dataclassabc import dataclassabc

from polymat.typing import VariableVectorExpression, ScalarPolynomialExpression

from sosopt.coneconstraints.equalityconstraint import init_equality_constraint
from sosopt.polynomialconstraints.constraintprimitive.constraintprimitive import (
    ConstraintPrimitive,
)
from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol


@dataclassabc(frozen=True, slots=True)
class ZeroPolynomialPrimitive(ConstraintPrimitive):
    name: str
    expression: ScalarPolynomialExpression
    polynomial_variables: VariableVectorExpression
    decision_variable_symbols: tuple[DecisionVariableSymbol, ...]

    def copy(self, /, **others):
        return replace(self, **others)
    
    @override
    def to_cone_constraint(self):
        return init_equality_constraint(
            name=self.name,
            expression=self.expression.to_linear_coefficients(self.polynomial_variables).T,
            decision_variable_symbols=self.decision_variable_symbols,
        )


def init_zero_polynomial_primitive(
    name: str,
    expression: ScalarPolynomialExpression,
    polynomial_variables: VariableVectorExpression,
    decision_variable_symbols: tuple[DecisionVariableSymbol, ...],
):
    return ZeroPolynomialPrimitive(
        name=name,
        expression=expression,
        polynomial_variables=polynomial_variables,
        decision_variable_symbols=decision_variable_symbols,
    )
