from abc import abstractmethod

import polymat
from polymat.typing import (
    MatrixExpression,
    MonomialVectorExpression,
    VariableVectorExpression,
)

from sosopt.polymat.decisionvariableexpression import DecisionVariableExpression


class PolynomialMatrixVariable(MatrixExpression):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def coefficients(self) -> tuple[tuple[DecisionVariableExpression]]: ...

    @property
    @abstractmethod
    def monomials(self) -> MonomialVectorExpression: ...

    # @property
    # @abstractmethod
    # def polynomial_variables(self) -> VariableVectorExpression: ...

    @property
    @abstractmethod
    def shape(self) -> tuple[int, int]: ...

    def iterate_coefficients(self):
        n_rows, n_cols = self.shape

        for row in range(n_rows):
            for col in range(n_cols):
                yield (row, col), self.coefficients[row][col]

    def iterate_symbols(self):
        for _, variable in self.iterate_coefficients():
            yield variable.symbol

    def to_coefficient_vector(self) -> VariableVectorExpression:
        return polymat.v_stack(v for _, v in self.iterate_coefficients())


PolynomialMatrixVariable = PolynomialMatrixVariable
PolynomialSymmetricMatrixVariable = PolynomialMatrixVariable
PolynomialVectorVariable = PolynomialMatrixVariable
PolynomialRowVectorVariable = PolynomialMatrixVariable
PolynomialVariable = PolynomialMatrixVariable
