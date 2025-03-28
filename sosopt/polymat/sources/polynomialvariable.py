from abc import abstractmethod
from typing import Iterable, override

import polymat
from polymat.typing import (
    MatrixExpression,
    MonomialVectorExpression,
    VariableVectorExpression,
    VariableExpression,
)

from sosopt.polymat.sources.decisionvariableexpression import DecisionVariableVectorSymbolExpression


class PolynomialVariable[_](MatrixExpression):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def monomials(self) -> MonomialVectorExpression: ...

    @abstractmethod
    def iterate_coefficients(self) -> Iterable[tuple[tuple[int, int], VariableExpression]]:
        ...

    def iterate_symbols(self):
        for _, variable in self.iterate_coefficients():
            yield variable.symbol

    def to_coefficient_vector(self) -> VariableVectorExpression:
        return polymat.v_stack(v for _, v in self.iterate_coefficients())


class PolynomialMatrixVariable[_](PolynomialVariable):
    @property
    @abstractmethod
    def coefficients(self) -> tuple[tuple[DecisionVariableVectorSymbolExpression]]: ...

    @property
    @abstractmethod
    def shape(self) -> tuple[int, int]: ...

    @override
    def iterate_coefficients(self):
        n_rows, n_cols = self.shape

        for row in range(n_rows):
            for col in range(n_cols):
                yield (row, col), self.coefficients[row][col]
    

class ScalarPolynomialVariable[_](PolynomialVariable):
    @property
    @abstractmethod
    def coefficient(self) -> DecisionVariableVectorSymbolExpression: ...

    def iterate_coefficients(self):
        yield (0, 0), self.coefficient

    @property
    def symbol(self):
        return self.coefficient.symbol


PolynomialSymmetricMatrixVariable = PolynomialMatrixVariable
PolynomialVectorVariable = PolynomialMatrixVariable
PolynomialRowVectorVariable = PolynomialMatrixVariable
