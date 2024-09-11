from __future__ import annotations

from abc import abstractmethod
from typing import override

import polymat
from polymat.typing import (
    VectorExpression,
)

from sosopt.constraints.constraintprimitives.constraintprimitive import (
    LinearConstraintPrimitive,
)
from sosopt.constraints.utils.polynomialvariablesmixin import PolynomialVariablesMixin


class ZeroPolynomialPrimitive(
    PolynomialVariablesMixin, LinearConstraintPrimitive
):
    @property
    @override
    @abstractmethod
    def condition(self) -> VectorExpression: ...

    @property
    @abstractmethod
    def n_rows(self) -> int: ...

    @override
    def to_constraint_vector(self) -> VectorExpression:
        def gen_linear_equations():
            for row in range(self.n_rows):
                yield self.condition[row, 0].to_linear_coefficients(self.polynomial_variables).T

        return polymat.v_stack(gen_linear_equations()).filter_non_zero()
