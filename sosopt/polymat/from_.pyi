from typing import overload

from statemonad.typing import StateMonad

from polymat.typing import (
    State as BaseState,
    MatrixExpression,
    VariableVectorExpression,
    MonomialVectorExpression,
    SymmetricMatrixExpression,
    ScalarPolynomialExpression,
)

from sosopt.polymat.symbols.auxiliaryvariablesymbol import AuxiliaryVariableSymbol
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

def gram_matrix[State: BaseState](
    expression: ScalarPolynomialExpression[State],
    variables: VariableVectorExpression[State],
    monomials: MonomialVectorExpression[State] | None = None,
    auxilliary_variable_symbol: AuxiliaryVariableSymbol | None = None,
    sparse_smr: bool | None = None,
) -> SymmetricMatrixExpression[State]: ...

def sos_monomial_basis[State: BaseState](
    expression: MatrixExpression[State],
    variables: VariableVectorExpression[State],
    sparse_smr: bool | None = None,
) -> MonomialVectorExpression[State]: ...

class define_multiplier[State: BaseState]:
    def __new__(
        _,
        name: str,
        degree: int | MatrixExpression[State],
        multiplicand: MatrixExpression[State],
        variables: VariableVectorExpression[State] | tuple[int, ...],
    ) -> StateMonad[State, PolynomialMatrixVariable[State]]: ...

class define_polynomial[State: BaseState]:
    @overload
    def __new__(
        _, name: str
    ) -> StateMonad[State, ScalarPolynomialVariable[State]]: ...
    @overload
    def __new__(
        _, name: str, monomials: MonomialVectorExpression
    ) -> StateMonad[State, ScalarPolynomialVariable[State]]: ...
    @overload
    def __new__(
        _, name: str, n_rows: int
    ) -> StateMonad[State, PolynomialVectorVariable[State]]: ...
    @overload
    def __new__(
        _, name: str, monomials: MonomialVectorExpression, n_rows: int
    ) -> StateMonad[State, PolynomialVectorVariable[State]]: ...
    @overload
    def __new__(
        _, name: str, n_cols: int,
    ) -> StateMonad[State, PolynomialRowVectorVariable[State]]: ...
    @overload
    def __new__(
        _, name: str, monomials: MonomialVectorExpression, n_cols: int
    ) -> StateMonad[State, PolynomialRowVectorVariable[State]]: ...
    @overload
    def __new__(
        _, name: str, n_rows: int, n_cols: int
    ) -> StateMonad[State, PolynomialMatrixVariable[State]]: ...
    @overload
    def __new__(
        _, name: str, monomials: MonomialVectorExpression, n_rows: int, n_cols: int
    ) -> StateMonad[State, PolynomialMatrixVariable[State]]: ...

class define_symmetric_matrix[State: BaseState]:
    @overload
    def __new__(
        _,
        name: str,
        size: int,
    ) -> StateMonad[State, PolynomialSymmetricMatrixVariable[State]]: ...
    @overload
    def __new__(
        _,
        name: str,
        monomials: MonomialVectorExpression,
        size: int,
    ) -> StateMonad[State, PolynomialSymmetricMatrixVariable[State]]: ...

class define_variable[State: BaseState]:
    @overload
    def __new__(_, name: str) -> DecisionVariableExpression[State]: ...
    @overload
    def __new__(
        _,
        name: str,
        size: int | MatrixExpression[State],
    ) -> DecisionVariableVectorSymbolExpression[State]: ...



# def v_stack(
#     expressions: Iterator[DecisionVariableVectorSymbolExpression],
# ) -> VariableVectorExpression: ...
