from __future__ import annotations

from abc import abstractmethod
from typing import override

from polymat.typing import (
    PolynomialExpression,
    VectorExpression,
)

from sosopt.constraints.constraintprimitives.constraintprimitive import (
    SDPConstraintPrimitive,
)
from sosopt.constraints.utils.polynomialvariablesmixin import PolynomialVariablesMixin


class PositivePolynomialPrimitive(PolynomialVariablesMixin, SDPConstraintPrimitive):
    @property
    @override
    @abstractmethod
    def condition(self) -> PolynomialExpression: ...

    @property
    def gram_matrix(self):
        return self.condition.to_gram_matrix(self.polynomial_variables)

    @override
    def to_constraint_vector(self) -> VectorExpression:
        return self.gram_matrix.reshape(-1, 1).to_vector()
