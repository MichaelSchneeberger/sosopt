from typing import Iterator, overload

from statemonad.typing import StateMonad

from polymat.typing import (
    State,
    MatrixExpression,
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
from sosopt.polymat.decisionvariableexpression import (
    DecisionVariableExpression,
    SingleValueDecisionVariableExpression,
)

def define_multiplier(
    name: str,
    degree: int,
    multiplicand: MatrixExpression,
    variables: VariableVectorExpression,
) -> StateMonad[State, PolynomialVariable]: ...
@overload
def define_polynomial(
    name: str,
    monomials: MonomialVectorExpression,
    polynomial_variables: VariableVectorExpression,
) -> PolynomialVariable: ...
@overload
def define_polynomial(
    name: str,
    monomials: MonomialVectorExpression,
    polynomial_variables: VariableVectorExpression,
    n_row: int,
) -> PolynomialVectorVariable: ...
@overload
def define_polynomial(
    name: str,
    monomials: MonomialVectorExpression,
    polynomial_variables: VariableVectorExpression,
    n_col: int,
) -> PolynomialRowVectorVariable: ...
@overload
def define_polynomial(
    name: str,
    monomials: MonomialVectorExpression,
    polynomial_variables: VariableVectorExpression,
    n_row: int,
    n_col: int,
) -> PolynomialMatrixVariable: ...
@overload
def define_symmetric_matrix(
    name: str,
    size: int,
) -> PolynomialSymmetricMatrixVariable: ...
@overload
def define_symmetric_matrix(
    name: str,
    monomials: MonomialVectorExpression,
    polynomial_variables: VariableVectorExpression,
    size: int,
) -> PolynomialSymmetricMatrixVariable: ...
@overload
def define_variable(
    name: str,
) -> SingleValueDecisionVariableExpression: ...
@overload
def define_variable(
    name: str,
    size: int | MatrixExpression | None = None,
) -> DecisionVariableExpression: ...
def v_stack(
    expressions: Iterator[DecisionVariableExpression],
) -> VariableVectorExpression: ...
