from abc import abstractmethod

from polymat.typing import (
    MatrixExpression,
    MonomialVectorExpression,
    VariableVectorExpression,
)

from sosopt.polymat.decisionvariableexpression import DecisionVariableExpression


class PolynomialVariable(MatrixExpression):
    @property
    @abstractmethod
    def coefficients(self) -> tuple[tuple[DecisionVariableExpression]]: ...

    @property
    @abstractmethod
    def monomials(self) -> MonomialVectorExpression: ...

    @property
    @abstractmethod
    def polynomial_variables(self) -> VariableVectorExpression: ...

    @property
    @abstractmethod
    def n_row(self) -> int: ...

    @property
    @abstractmethod
    def n_col(self) -> int: ...

    @property
    @abstractmethod
    def name(self) -> str: ...

    def iterate_coefficients(self):
        for row in range(self.n_row):
            for col in range(self.n_col):
                yield (row, col), self.coefficients[row][col]

    def to_symbols(self):
        for _, variable in self.iterate_coefficients():
            yield variable.symbol
