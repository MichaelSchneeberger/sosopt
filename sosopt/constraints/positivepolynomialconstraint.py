from __future__ import annotations
from abc import abstractmethod
from typing import override

from polymat.typing import PolynomialExpression

from sosopt.constraints.constraint import Constraint
from sosopt.constraints.constraintprimitives.constraintprimitive import (
    ConstraintPrimitive,
)
from sosopt.constraints.constraintprimitives.init import (
    init_positive_polynomial_primitive,
)
from sosopt.constraints.utils.polynomialvariablesmixin import PolynomialVariablesMixin


class PositivePolynomialConstraint(PolynomialVariablesMixin, Constraint):
    @property
    @abstractmethod
    def condition(self) -> PolynomialExpression: ...

    @override
    def get_constraint_primitives(
        self,
    ) -> tuple[ConstraintPrimitive, ...]:
        primitive = init_positive_polynomial_primitive(
            name=self.name,
            children=tuple(),  # no children
            condition=self.condition,
            decision_variable_symbols=self.decision_variable_symbols,
            volatile_symbols=tuple(),
            polynomial_variables=self.polynomial_variables,
        )
        return (primitive,)
