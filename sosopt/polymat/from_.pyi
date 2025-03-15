from typing import Iterator, overload

from statemonad.typing import StateMonad

from polymat.typing import (
    State,
    MatrixExpression,
    VariableVectorExpression,
    MonomialVectorExpression,
    SymmetricMatrixExpression,
)

from sosopt.state.state import State as SOSOptState
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

def quadratic_coefficients(
    expression: MatrixExpression,
    variables: VariableVectorExpression,
    monomials: MonomialVectorExpression | None = None,
) -> SymmetricMatrixExpression[SOSOptState]: ...
def define_multiplier(
    name: str,
    degree: int,
    multiplicand: MatrixExpression,
    variables: VariableVectorExpression,
) -> StateMonad[State, PolynomialVariable]: ...
@overload
def define_polynomial(
    name: str,
) -> PolynomialVariable: ...
@overload
def define_polynomial(
    name: str,
    monomials: MonomialVectorExpression,
) -> PolynomialVariable: ...
@overload
def define_polynomial(
    name: str,
    n_rows: int,
) -> PolynomialVectorVariable: ...
@overload
def define_polynomial(
    name: str,
    monomials: MonomialVectorExpression,
    n_rows: int,
) -> PolynomialVectorVariable: ...
@overload
def define_polynomial(
    name: str,
    n_cols: int,
) -> PolynomialRowVectorVariable: ...
@overload
def define_polynomial(
    name: str,
    monomials: MonomialVectorExpression,
    n_cols: int,
) -> PolynomialRowVectorVariable: ...
@overload
def define_polynomial(
    name: str,
    n_rows: int,
    n_cols: int,
) -> PolynomialMatrixVariable: ...
@overload
def define_polynomial(
    name: str,
    monomials: MonomialVectorExpression,
    n_rows: int,
    n_cols: int,
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
