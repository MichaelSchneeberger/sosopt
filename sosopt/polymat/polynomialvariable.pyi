from typing import Iterable

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
from sosopt.polymat.decisionvariableexpression import (
    DecisionVariableVectorSymbolExpression,
)
from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol

class PolynomialVariable[State: BaseState](MatrixExpression):
    name: str
    monomials: MonomialVectorExpression[State]

    def iterate_coefficients(
        self,
    ) -> Iterable[DecisionVariableVectorSymbolExpression[State]]: ...
    def iterate_symbols(self) -> Iterable[DecisionVariableSymbol]: ...
    def to_coefficient_vector(self) -> VariableVectorExpression[State]: ...

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
