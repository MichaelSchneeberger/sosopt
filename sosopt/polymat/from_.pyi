from typing import Iterator, overload

from sosopt.polymat.symbols.auxiliaryvariablesymbol import AuxiliaryVariableSymbol
from statemonad.typing import StateMonad

from polymat.typing import (
    State as BaseState,
    MatrixExpression,
    VariableVectorExpression,
    MonomialVectorExpression,
    SymmetricMatrixExpression,
)

# from sosopt.state.state import State as BaseState
from sosopt.polymat.sources.polynomialvariable import (
    PolynomialMatrixVariable,
    ScalarPolynomialVariable,
    PolynomialRowVectorVariable,
    PolynomialVectorVariable,
    PolynomialSymmetricMatrixVariable,
)
from sosopt.polymat.sources.decisionvariableexpression import (
    DecisionVariableVectorSymbolExpression,
    DecisionVariableExpression,
)


def square_matricial_representation(
    expression: MatrixExpression,
    variables: VariableVectorExpression,
    monomials: MonomialVectorExpression | None = None,
    auxilliary_variable_symbol: AuxiliaryVariableSymbol | None = None,
) -> SymmetricMatrixExpression: ...

def square_matricial_representation_sparse(
    expression: MatrixExpression,
    variables: VariableVectorExpression,
    monomials: MonomialVectorExpression | None = None,
) -> SymmetricMatrixExpression: ...

def quadratic_monomial_vector(
    expression: MatrixExpression,
    variables: VariableVectorExpression,
) -> MonomialVectorExpression: ...

def quadratic_monomial_vector_sparse(
    expression: MatrixExpression,
    variables: VariableVectorExpression,
) -> MonomialVectorExpression: ...

class define_multiplier[State: BaseState]:
    def __new__(
        _, 
        name: str,
        degree: int,
        multiplicand: MatrixExpression[State],
        variables: VariableVectorExpression[State] | tuple[int, ...],
    ) -> StateMonad[State, PolynomialMatrixVariable[State]]: ...

class define_polynomial[State: BaseState]:
    @overload
    def __new__(_, name: str) -> ScalarPolynomialVariable[State]: ...
    @overload
    def __new__(
        _, name: str, monomials: MonomialVectorExpression
    ) -> ScalarPolynomialVariable[State]: ...
    @overload
    def __new__(
        _, name: str, n_rows: int
    ) -> PolynomialVectorVariable[State]: ...
    @overload
    def __new__(
        _, name: str, monomials: MonomialVectorExpression, n_rows: int
    ) -> PolynomialVectorVariable[State]: ...
    @overload
    def __new__(
        _, name: str, n_cols: int
    ) -> PolynomialRowVectorVariable[State]: ...
    @overload
    def __new__(
        _, name: str, monomials: MonomialVectorExpression, n_cols: int
    ) -> PolynomialRowVectorVariable[State]: ...
    @overload
    def __new__(
        _, name: str, n_rows: int, n_cols: int
    ) -> PolynomialMatrixVariable[State]: ...
    @overload
    def __new__(
        _, name: str, monomials: MonomialVectorExpression, n_rows: int, n_cols: int
    ) -> PolynomialMatrixVariable[State]: ...

class define_symmetric_matrix[State: BaseState]:
    @overload
    def __new__(
        _, name: str, size: int,
    ) -> PolynomialSymmetricMatrixVariable[State]: ...
    @overload
    def __new__(
        _, name: str, monomials: MonomialVectorExpression, size: int,
    ) -> PolynomialSymmetricMatrixVariable[State]: ...

class define_variable[State: BaseState]:
    @overload
    def __new__(_, name: str) -> DecisionVariableExpression[State]: ...
    @overload
    def __new__(
        _,
        name: str,
        size: int | MatrixExpression[State],
    ) -> DecisionVariableVectorSymbolExpression[State]: ...

def v_stack(
    expressions: Iterator[DecisionVariableVectorSymbolExpression],
) -> VariableVectorExpression: ...
