from typing import override
from dataclasses import replace
from dataclassabc import dataclassabc

from polymat.typing import (
    ExpressionNode,
    VariableExpression,
    MonomialVectorExpression,
)

from sosopt.polymat.decisionvariableexpression import DecisionVariableExpression
from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol
from sosopt.polymat.polynomialvariable import PolynomialVariable


@dataclassabc(frozen=True, slots=True)
class DecisionVariableExpressionImpl(DecisionVariableExpression):
    child: ExpressionNode
    symbol: DecisionVariableSymbol

    @override
    def copy(self, /, **changes):
        return replace(self, **changes)


def init_decision_variable_expression(child: ExpressionNode, symbol: DecisionVariableSymbol):
    return DecisionVariableExpressionImpl(
        child=child,
        symbol=symbol,
    )


@dataclassabc(frozen=True, slots=True)
class PolynomialVariableImpl(PolynomialVariable):
    name: str
    child: ExpressionNode
    coefficients: tuple[tuple[VariableExpression]]
    shape: tuple[int, int]
    monomials: MonomialVectorExpression

    @override
    def copy(self, /, **changes):
        return replace(self, **changes)


def init_polynomial_variable(
    name: str,
    child: ExpressionNode,
    coefficients: tuple[tuple[VariableExpression]],
    monomials: MonomialVectorExpression,
    shape: tuple[int, int] = (1, 1),
):
    return PolynomialVariableImpl(
        name=name,
        monomials=monomials,
        coefficients=coefficients,
        child=child,
        shape=shape,
    )
