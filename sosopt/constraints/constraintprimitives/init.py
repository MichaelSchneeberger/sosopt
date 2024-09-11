from dataclasses import replace
from dataclassabc import dataclassabc

from polymat.typing import MatrixExpression, VariableVectorExpression

from sosopt.constraints.constraintprimitives.constraintprimitive import (
    ConstraintPrimitive,
)
from sosopt.constraints.constraintprimitives.positivepolynomialprimitive import (
    PositivePolynomialPrimitive,
)
from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol


@dataclassabc(frozen=True, slots=True)
class PositivePolynomialPrimitiveImpl(PositivePolynomialPrimitive):
    name: str
    condition: MatrixExpression
    children: tuple[ConstraintPrimitive, ...]
    decision_variable_symbols: tuple[DecisionVariableSymbol, ...]
    polynomial_variables: VariableVectorExpression

    def copy(self, /, **others):
        return replace(self, **others)


init_positive_polynomial_primitive = (
    PositivePolynomialPrimitiveImpl
)
