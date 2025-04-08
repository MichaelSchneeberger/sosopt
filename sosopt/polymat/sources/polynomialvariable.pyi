from typing import Iterable

from statemonad.typing import StateMonad

from polymat.typing import (
    State as BaseState,
    MatrixExpression,
    VectorExpression,
    RowVectorExpression,
    ScalarPolynomialExpression,
    SymmetricMatrixExpression,
    MonomialVectorExpression,
    VariableVectorExpression,
)

# from sosopt.state.state import State as BaseState
from sosopt.polymat.sources.decisionvariableexpression import (
    DecisionVariableVectorSymbolExpression,
)
from sosopt.polymat.symbols.decisionvariablesymbol import DecisionVariableSymbol

class PolynomialVariable[State: BaseState](MatrixExpression):
    name: str
    monomials: MonomialVectorExpression[State]

    def iterate_coefficients(
        self,
    ) -> Iterable[tuple[tuple[int, int], DecisionVariableVectorSymbolExpression[State]]]: ...
    def iterate_symbols(self) -> Iterable[DecisionVariableSymbol]: ...
    def to_coefficient_vector(self) -> VariableVectorExpression[State]: ...
    # def to_symbol_values(self, value: MatrixExpression) -> StateMonad[State, dict[DecisionVariableSymbol, tuple[float, ...]]]: ...

class PolynomialMatrixVariable[State: BaseState](PolynomialVariable):
    coefficients: tuple[tuple[DecisionVariableVectorSymbolExpression[State]]]
    shape: tuple[int, int]

class PolynomialSymmetricMatrixVariable[State: BaseState](
    PolynomialMatrixVariable[State], 
    SymmetricMatrixExpression[State],
): ...
class PolynomialVectorVariable[State: BaseState](
    PolynomialMatrixVariable[State], 
    VectorExpression[State],
): ...
class PolynomialRowVectorVariable[State: BaseState](
    PolynomialMatrixVariable[State], 
    RowVectorExpression[State],
): ...

class ScalarPolynomialVariable[State: BaseState](
    PolynomialVectorVariable[State], 
    PolynomialVariable[State], 
    ScalarPolynomialExpression[State],
):
    coefficients: DecisionVariableVectorSymbolExpression[State]
