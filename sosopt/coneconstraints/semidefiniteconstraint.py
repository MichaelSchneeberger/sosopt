from dataclasses import replace
from dataclassabc import dataclassabc

from polymat.typing import SymmetricMatrixExpression, VectorExpression

from sosopt.coneconstraints.coneconstraint import ConeConstraint
from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol


@dataclassabc(frozen=True, slots=True)
class SemiDefiniteConstraint(ConeConstraint):
    name: str
    expression: SymmetricMatrixExpression
    decision_variable_symbols: tuple[DecisionVariableSymbol, ...]

    def copy(self, /, **others):
        return replace(self, **others)

    def to_vector(self) -> VectorExpression:
        return self.expression.to_vector()


def init_semi_definite_constraint(
    name: str,
    expression: SymmetricMatrixExpression,
    decision_variable_symbols: tuple[DecisionVariableSymbol, ...],
):
    return SemiDefiniteConstraint(
        name=name,
        expression=expression,
        decision_variable_symbols=decision_variable_symbols,
    )

