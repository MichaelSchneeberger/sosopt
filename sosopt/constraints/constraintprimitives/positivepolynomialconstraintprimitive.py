from __future__ import annotations

from abc import abstractmethod
from typing import override

from statemonad.typing import StateMonad

import polymat
from polymat.typing import (
    ArrayRepr,
    State,
    PolynomialExpression,
)

from sosopt.constraints.constraintprimitives.constraintprimitive import (
    ConstraintPrimitive,
)
from sosopt.constraints.polynomialvariablesmixin import PolynomialVariablesMixin
from sosopt.utils.grammatrix import to_gram_matrix


class PositivePolynomialConstraintPrimitive(
    PolynomialVariablesMixin, ConstraintPrimitive
):
    @property
    @override
    @abstractmethod
    def condition(self) -> PolynomialExpression: ...

    @property
    def gram_matrix(self):
        return to_gram_matrix(self.condition, self.polynomial_variables)

    def to_array(
        self, indices: tuple[int, ...]
    ) -> StateMonad[State, ArrayRepr]:
        return polymat.to_array(
            self.gram_matrix.reshape(-1, 1).to_vector(), 
            variables=indices
        )
