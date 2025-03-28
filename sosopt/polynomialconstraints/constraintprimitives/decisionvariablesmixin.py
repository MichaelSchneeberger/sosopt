from abc import ABC, abstractmethod

from sosopt.state.state import State
import statemonad

import polymat
from polymat.typing import MatrixExpression

from sosopt.polymat.symbols.decisionvariablesymbol import DecisionVariableSymbol


class DecisionVariablesMixin(ABC):
    @property
    @abstractmethod
    def decision_variable_symbols(self) -> tuple[DecisionVariableSymbol, ...]: ...


def to_decision_variable_symbols(expr: MatrixExpression):
    def _to_decision_variable_symbols(state: State):
        state, variable_indices = polymat.to_variable_indices(expr).apply(state)

        def gen_decision_variable_symbols():
            for index in variable_indices:
                match symbol := state.get_symbol(index=index):
                    case DecisionVariableSymbol():
                        yield symbol

        return state, tuple(set(gen_decision_variable_symbols()))

    return statemonad.get_map_put(_to_decision_variable_symbols)