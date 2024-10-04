from __future__ import annotations

from dataclasses import replace
from typing import override

from dataclassabc import dataclassabc

from polymat.typing import VariableVectorExpression, PolynomialExpression

from sosopt.coneconstraints.equalityconstraint import init_equality_constraint
from sosopt.polynomialconstraints.constraintprimitive.constraintprimitive import (
    ConstraintPrimitive,
)
from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol


@dataclassabc(frozen=True, slots=True)
class ZeroPolynomialPrimitive(ConstraintPrimitive):
    name: str
    expression: PolynomialExpression
    polynomial_variables: VariableVectorExpression
    decision_variable_symbols: tuple[DecisionVariableSymbol, ...]

    def copy(self, /, **others):
        return replace(self, **others)
    
    @override
    def to_cone_constraint(self):
        return init_equality_constraint(
            name=self.name,
            expression=self.expression.to_linear_coefficients(self.polynomial_variables).T,
            decision_variable_symbols=self.decision_variable_symbols,
        )


def init_zero_polynomial_primitive(
    name: str,
    expression: PolynomialExpression,
    polynomial_variables: VariableVectorExpression,
    decision_variable_symbols: tuple[DecisionVariableSymbol, ...],
):
    return ZeroPolynomialPrimitive(
        name=name,
        expression=expression,
        polynomial_variables=polynomial_variables,
        decision_variable_symbols=decision_variable_symbols,
    )

# class EqualityConstraint(
#     PolynomialVariablesMixin, EqualityConstraint
# ):
#     @property
#     @override
#     @abstractmethod
#     def condition(self) -> VectorExpression: ...

#     @property
#     @abstractmethod
#     def shape(self) -> tuple[int, int]: ...

#     @override
#     def to_constraint_vector(self) -> VectorExpression:
#         def gen_linear_equations():
#             n_rows, n_cols = self.shape

#             for row in range(n_rows):
#                 for col in range(n_cols):
#                     yield self.condition[row, col].to_linear_coefficients(self.polynomial_variables).T

#         return polymat.v_stack(gen_linear_equations()).filter_non_zero()
