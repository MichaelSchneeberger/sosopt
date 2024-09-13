from dataclasses import replace
from dataclassabc import dataclassabc

from polymat.typing import MatrixExpression, VariableVectorExpression

from sosopt.constraints.constraintprimitives.constraintprimitive import (
    ConstraintPrimitive,
)
from sosopt.constraints.constraintprimitives.sumofsquaresprimitive import (
    SumOfSqauresPrimitive,
)
from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol


@dataclassabc(frozen=True, slots=True)
class SumOfSqauresPrimitiveImpl(SumOfSqauresPrimitive):
    name: str
    condition: MatrixExpression
    children: tuple[ConstraintPrimitive, ...]
    decision_variable_symbols: tuple[DecisionVariableSymbol, ...]
    polynomial_variables: VariableVectorExpression

    def copy(self, /, **others):
        return replace(self, **others)


def init_sum_of_squares_primitive(
    name: str,
    condition: MatrixExpression,
    children: tuple[ConstraintPrimitive, ...],
    decision_variable_symbols: tuple[DecisionVariableSymbol, ...],
    polynomial_variables: VariableVectorExpression,
):
    return SumOfSqauresPrimitiveImpl(
        name=name,
        condition=condition,
        children=children,
        decision_variable_symbols=decision_variable_symbols,
        polynomial_variables=polynomial_variables,
    )
