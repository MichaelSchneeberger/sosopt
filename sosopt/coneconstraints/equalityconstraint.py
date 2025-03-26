from dataclasses import replace
from dataclassabc import dataclassabc

import statemonad

from polymat.typing import VectorExpression, State

from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol
from sosopt.coneconstraints.anonymousvariablesmixin import to_anonymous_variable_indices
from sosopt.coneconstraints.coneconstraint import ConeConstraint


@dataclassabc(frozen=True, slots=True)
class EqualityConstraint(ConeConstraint):
    name: str
    expression: VectorExpression
    decision_variable_symbols: tuple[DecisionVariableSymbol, ...]
    anonymous_variable_indices: tuple[int, ...]

    def to_vector(self) -> VectorExpression:
        return self.expression

    def copy(self, /, **others):
        return replace(self, **others)


def init_equality_constraint(
    name: str,
    expression: VectorExpression,
    decision_variable_symbols: tuple[DecisionVariableSymbol, ...],
):
    def _init_equality_constraint(state: State):
        state, anonymous_variable_indices = to_anonymous_variable_indices(expression).apply(state)
 
        return state, EqualityConstraint(
            name=name,
            expression=expression,
            decision_variable_symbols=decision_variable_symbols,
            anonymous_variable_indices=anonymous_variable_indices,
        )

    return statemonad.get_map_put(_init_equality_constraint)
