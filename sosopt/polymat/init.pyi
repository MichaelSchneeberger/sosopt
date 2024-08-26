from typing import overload

from polymat.typing import (
    ExpressionTreeMixin,
    VariableVectorExpression,
    MonomialVectorExpression,
)

from sosopt.polymat.abc import (
    PolynomialMatrixVariable,
    PolynomialVariable,
    PolynomialRowVectorVariable,
    PolynomialVectorVariable,
)
from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol
from sosopt.polymat.decisionvariableexpression import DecisionVariableExpression

def init_decision_variable_expression(
    child: ExpressionTreeMixin, variable: DecisionVariableSymbol
) -> DecisionVariableExpression: ...
@overload
def init_polynomial_variable(
    name: str,
    monomials: MonomialVectorExpression,
    polynomial_variables: VariableVectorExpression,
) -> PolynomialVariable: ...
@overload
def init_polynomial_variable(
    name: str,
    monomials: MonomialVectorExpression,
    polynomial_variables: VariableVectorExpression,
    n_row: int,
) -> PolynomialVectorVariable: ...
@overload
def init_polynomial_variable(
    name: str,
    monomials: MonomialVectorExpression,
    polynomial_variables: VariableVectorExpression,
    n_col: int,
) -> PolynomialRowVectorVariable: ...
@overload
def init_polynomial_variable(
    name: str,
    monomials: MonomialVectorExpression,
    polynomial_variables: VariableVectorExpression,
    n_row: int,
    n_col: int,
) -> PolynomialMatrixVariable: ...
