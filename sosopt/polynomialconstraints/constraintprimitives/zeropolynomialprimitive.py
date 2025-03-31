from __future__ import annotations

from dataclasses import replace
from typing import override

from dataclassabc import dataclassabc

from polymat.typing import ScalarPolynomialExpression

from sosopt.coneconstraints.equalityconstraint import init_equality_constraint
from sosopt.polynomialconstraints.constraintprimitives.polynomialconstraintprimitive import (
    PolynomialConstraintPrimitive,
)
from sosopt.polymat.symbols.decisionvariablesymbol import DecisionVariableSymbol
from sosopt.polynomialconstraints.polynomialvariablesmixin import PolynomialVariablesMixin


@dataclassabc(frozen=True, slots=True)
class ZeroPolynomialPrimitive(PolynomialVariablesMixin, PolynomialConstraintPrimitive):
    name: str | None
    expression: ScalarPolynomialExpression
    polynomial_variable_indices: tuple[int, ...]
    decision_variable_symbols: tuple[DecisionVariableSymbol, ...]

    def copy(self, /, **others):
        return replace(self, **others)
    
    @override
    def to_cone_constraint(self):
        return init_equality_constraint(
            name=self.name,
            expression=self.expression.to_linear_coefficients(self.polynomial_variable).T,
            # decision_variable_symbols=self.decision_variable_symbols,
        )


def init_zero_polynomial_primitive(
    name: str | None,
    expression: ScalarPolynomialExpression,
    polynomial_variable_indices: tuple[int, ...],
    decision_variable_symbols: tuple[DecisionVariableSymbol, ...],
):
    return ZeroPolynomialPrimitive(
        name=name,
        expression=expression,
        polynomial_variable_indices=polynomial_variable_indices,
        decision_variable_symbols=decision_variable_symbols,
    )
