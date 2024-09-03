from typing import Iterable

from polymat.typing import (
    MatrixExpression,
    VectorExpression,
    RowVectorExpression,
    PolynomialExpression,
    SymmetricMatrixExpression,
    MonomialVectorExpression,
    VariableVectorExpression,
)

from sosopt.polymat.decisionvariableexpression import DecisionVariableExpression
from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol

class PolynomialMatrixVariable(MatrixExpression):
    name: str
    coefficients: tuple[tuple[DecisionVariableExpression]]
    monomials: MonomialVectorExpression
    polynomial_variables: VariableVectorExpression
    shape: tuple[int, int]

    def iterate_coefficients(
        self,
    ) -> Iterable[tuple[tuple[int, int], DecisionVariableExpression]]: ...
    def iterate_symbols(self) -> Iterable[DecisionVariableSymbol]: ...
    def to_coefficient_vector(self) -> VariableVectorExpression: ...

class PolynomialSymmetricMatrixVariable(
    PolynomialMatrixVariable, SymmetricMatrixExpression
): ...
class PolynomialVectorVariable(PolynomialMatrixVariable, VectorExpression): ...
class PolynomialRowVectorVariable(PolynomialMatrixVariable, RowVectorExpression): ...
class PolynomialVariable(PolynomialVectorVariable, PolynomialExpression): ...
