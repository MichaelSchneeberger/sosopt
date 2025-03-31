from dataclasses import replace
from dataclassabc import dataclassabc

import statemonad

from polymat.typing import SymmetricMatrixExpression, VectorExpression, State

from sosopt.polymat.symbols.conedecisionvariablesymbol import ConeDecisionVariableSymbol
from sosopt.coneconstraints.coneconstraint import ConeConstraint, to_decision_variable_symbols


@dataclassabc(frozen=True, slots=True)
class SemiDefiniteConstraint(ConeConstraint):
    name: str | None
    expression: SymmetricMatrixExpression
    decision_variable_symbols: tuple[ConeDecisionVariableSymbol, ...]

    def copy(self, /, **others):
        return replace(self, **others)

    def to_vector(self) -> VectorExpression:
        return self.expression.to_vector()


def init_semi_definite_constraint(
    name: str | None,
    expression: SymmetricMatrixExpression,
    decision_variable_symbols: tuple[ConeDecisionVariableSymbol, ...] | None = None,
):
    def _init_semi_definite_constraint(state: State, decision_variable_symbols=decision_variable_symbols):
        if decision_variable_symbols is None:
            state, decision_variable_symbols = to_decision_variable_symbols(expression).apply(state)

        return state, SemiDefiniteConstraint(
            name=name,
            expression=expression,
            decision_variable_symbols=decision_variable_symbols,
        )

    return statemonad.get_map_put(_init_semi_definite_constraint)

