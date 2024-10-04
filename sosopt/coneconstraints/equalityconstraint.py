from dataclasses import replace
from dataclassabc import dataclassabc

from polymat.typing import VectorExpression

from sosopt.coneconstraints.coneconstraint import ConeConstraint
from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol


@dataclassabc(frozen=True, slots=True)
class EqualityConstraint(ConeConstraint):
    name: str
    expression: VectorExpression
    decision_variable_symbols: tuple[DecisionVariableSymbol, ...]

    def to_vector(self) -> VectorExpression:
        return self.expression

    def copy(self, /, **others):
        return replace(self, **others)


def init_equality_constraint(
    name: str,
    expression: VectorExpression,
    decision_variable_symbols: tuple[DecisionVariableSymbol, ...],
):
    return EqualityConstraint(
        name=name,
        expression=expression,
        decision_variable_symbols=decision_variable_symbols,
    )
