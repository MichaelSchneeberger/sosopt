from dataclasses import replace
from dataclassabc import dataclassabc

from polymat.typing import MatrixExpression, VariableVectorExpression

from sosopt.coneconstraints.coneconstraint import (
    ConeConstraint,
)
from sosopt.coneconstraints.sumofsquaresconstraint import (
    SumOfSqauresConstraint,
)
from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol


@dataclassabc(frozen=True, slots=True)
class SumOfSqauresConstraintImpl(SumOfSqauresConstraint):
    name: str
    condition: MatrixExpression
    children: tuple[ConeConstraint, ...]
    decision_variable_symbols: tuple[DecisionVariableSymbol, ...]
    polynomial_variables: VariableVectorExpression

    def copy(self, /, **others):
        return replace(self, **others)


def init_sum_of_squares_constraint(
    name: str,
    condition: MatrixExpression,
    decision_variable_symbols: tuple[DecisionVariableSymbol, ...],
    polynomial_variables: VariableVectorExpression,
    children: tuple[ConeConstraint, ...] | None = None,
):
    if children is None:
        children = tuple()

    return SumOfSqauresConstraintImpl(
        name=name,
        condition=condition,
        children=children,
        decision_variable_symbols=decision_variable_symbols,
        polynomial_variables=polynomial_variables,
    )


# @dataclassabc(frozen=True, slots=True)
# class ZeroPolynomialPrimitiveImpl(ZeroPolynomialPrimitive):
#     pass

