from dataclasses import replace
from dataclassabc import dataclassabc

import statemonad

from polymat.typing import VectorExpression, State

from sosopt.polymat.symbols.conedecisionvariablesymbol import ConeDecisionVariableSymbol
from sosopt.coneconstraints.coneconstraint import ConeConstraint, to_decision_variable_symbols


@dataclassabc(frozen=True, slots=True)
class EqualityConstraint(ConeConstraint):
    name: str | None
    expression: VectorExpression
    decision_variable_symbols: tuple[ConeDecisionVariableSymbol, ...]

    def to_vector(self) -> VectorExpression:
        return self.expression

    def copy(self, /, **others):
        return replace(self, **others)


def init_equality_constraint(
    name: str | None,
    expression: VectorExpression,
    decision_variable_symbols: tuple[ConeDecisionVariableSymbol, ...] | None = None,
):
    def _init_equality_constraint(state: State, decision_variable_symbols=decision_variable_symbols):
        if decision_variable_symbols is None:
            state, decision_variable_symbols = to_decision_variable_symbols(expression).apply(state)
 
        return state, EqualityConstraint(
            name=name,
            expression=expression,
            decision_variable_symbols=decision_variable_symbols,
        )

    return statemonad.get_map_put(_init_equality_constraint)
