from dataclasses import replace
from dataclassabc import dataclassabc

from polymat.typing import MatrixExpression, VariableVectorExpression

from sosopt.constraints.constraintprimitives.constraintprimitive import (
    ConstraintPrimitive,
)
from sosopt.constraints.constraintprimitives.positivepolynomialconstraintprimitive import (
    PositivePolynomialConstraintPrimitive,
)
from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol


@dataclassabc(frozen=True)
class PositivePolynomialConstraintPrimitiveImpl(PositivePolynomialConstraintPrimitive):
    children: tuple[ConstraintPrimitive, ...]
    condition: MatrixExpression
    decision_variable_symbols: tuple[DecisionVariableSymbol, ...]
    volatile_symbols: tuple[DecisionVariableSymbol, ...]
    name: str
    polynomial_variables: VariableVectorExpression

    def copy(self, /, **others):
        return replace(self, **others)


init_positive_polynomial_constraint_primitive = (
    PositivePolynomialConstraintPrimitiveImpl
)
