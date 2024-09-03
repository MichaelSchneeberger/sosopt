from typing import overload

from polymat.typing import (
    ExpressionNode,
    VariableVectorExpression,
    MonomialVectorExpression,
)

from sosopt.polymat.polynomialvariable import (
    PolynomialMatrixVariable,
    PolynomialVariable,
    PolynomialRowVectorVariable,
    PolynomialVectorVariable,
    PolynomialSymmetricMatrixVariable,
)
from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol
from sosopt.polymat.decisionvariableexpression import DecisionVariableExpression

def init_decision_variable_expression(
    child: ExpressionNode, symbol: DecisionVariableSymbol
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
def init_symmetric_matrix_variable(
        name: str,
        monomials: MonomialVectorExpression,
        polynomial_variables: VariableVectorExpression,
        size: int,
) -> PolynomialSymmetricMatrixVariable: ...