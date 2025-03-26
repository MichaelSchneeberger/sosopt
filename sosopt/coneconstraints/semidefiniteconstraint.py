from dataclasses import replace
from dataclassabc import dataclassabc

import statemonad

from polymat.typing import SymmetricMatrixExpression, VectorExpression, State

from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol
from sosopt.coneconstraints.anonymousvariablesmixin import to_anonymous_variable_indices
from sosopt.coneconstraints.coneconstraint import ConeConstraint


@dataclassabc(frozen=True, slots=True)
class SemiDefiniteConstraint(ConeConstraint):
    name: str
    expression: SymmetricMatrixExpression
    decision_variable_symbols: tuple[DecisionVariableSymbol, ...]
    anonymous_variable_indices: tuple[int, ...]

    def copy(self, /, **others):
        return replace(self, **others)

    def to_vector(self) -> VectorExpression:
        return self.expression.to_vector()


def init_semi_definite_constraint(
    name: str,
    expression: SymmetricMatrixExpression,
    decision_variable_symbols: tuple[DecisionVariableSymbol, ...],
):

    def _init_semi_definite_constraint(state: State):
        state, anonymous_variable_indices = to_anonymous_variable_indices(expression).apply(state)

        # print(f'{name}: {anonymous_variable_indices}')

        return state, SemiDefiniteConstraint(
            name=name,
            expression=expression,
            decision_variable_symbols=decision_variable_symbols,
            anonymous_variable_indices=anonymous_variable_indices,
        )

    return statemonad.get_map_put(_init_semi_definite_constraint)

