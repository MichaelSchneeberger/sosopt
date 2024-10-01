from __future__ import annotations
from abc import abstractmethod
from typing import override

from polymat.typing import MatrixExpression

from sosopt.constraints.constraint import Constraint
from sosopt.constraints.constraintprimitives.constraintprimitive import (
    ConstraintPrimitive,
)
from sosopt.constraints.constraintprimitives.init import (
    init_sum_of_squares_primitive,
)
from sosopt.constraints.utils.polynomialvariablesmixin import PolynomialVariablesMixin


class SumOfSqauresConstraint(PolynomialVariablesMixin, Constraint):
    @property
    @abstractmethod
    def condition(self) -> MatrixExpression: ...

    @property
    @abstractmethod
    def shape(self) -> tuple[int, int]: ...

    @override
    def get_constraint_primitives(
        self,
    ) -> tuple[ConstraintPrimitive, ...]:
        
        def gen_primitives():
            n_rows, n_cols = self.shape
            for row in range(n_rows):
                for col in range(n_cols):
                    yield init_sum_of_squares_primitive(
                        name=self.name,
                        condition=self.condition[row, col],
                        decision_variable_symbols=self.decision_variable_symbols,
                        polynomial_variables=self.polynomial_variables,
                    )
                    
        return tuple(gen_primitives())
