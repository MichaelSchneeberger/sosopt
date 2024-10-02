from __future__ import annotations

from abc import abstractmethod
from typing import override

import polymat
from polymat.typing import (
    VectorExpression,
)

from sosopt.coneconstraints.coneconstraint import (
    EqualityConstraint,
)
from sosopt.utils.polynomialvariablesmixin import PolynomialVariablesMixin


class ZeroPolynomialConstraint(
    PolynomialVariablesMixin, EqualityConstraint
):
    @property
    @override
    @abstractmethod
    def condition(self) -> VectorExpression: ...

    @property
    @abstractmethod
    def shape(self) -> tuple[int, int]: ...

    @override
    def to_constraint_vector(self) -> VectorExpression:
        def gen_linear_equations():
            n_rows, n_cols = self.shape

            for row in range(n_rows):
                for col in range(n_cols):
                    yield self.condition[row, col].to_linear_coefficients(self.polynomial_variables).T

        return polymat.v_stack(gen_linear_equations()).filter_non_zero()
