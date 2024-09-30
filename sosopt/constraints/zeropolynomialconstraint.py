from __future__ import annotations
from abc import abstractmethod
from typing import override

import polymat
from polymat.typing import VectorExpression

from sosopt.constraints.constraint import Constraint
from sosopt.constraints.constraintprimitives.constraintprimitive import LinearConstraintPrimitive
from sosopt.constraints.utils.polynomialvariablesmixin import PolynomialVariablesMixin


class ZeroPolynomialConstraint(PolynomialVariablesMixin, LinearConstraintPrimitive, Constraint):
    @property
    @abstractmethod
    def condition(self) -> VectorExpression: ...

    @property
    @abstractmethod
    def shape(self) -> tuple[int, int]: ...

    @override
    def get_constraint_primitives(
        self,
    ):
        return (self,)
        # primitive = init_zero_polynomial_primitive(
        #     name=self.name,
        #     condition=self.condition,
        #     n_rows=self.n_rows,
        #     decision_variable_symbols=self.decision_variable_symbols,
        #     polynomial_variables=self.polynomial_variables,
        # )
        # return (primitive,)

    @override
    def to_constraint_vector(self) -> VectorExpression:
        def gen_linear_equations():
            n_rows, n_cols = self.shape

            for row in range(n_rows):
                for col in range(n_cols):
                    yield self.condition[row, col].to_linear_coefficients(self.polynomial_variables).T

        return polymat.v_stack(gen_linear_equations()).filter_non_zero()

