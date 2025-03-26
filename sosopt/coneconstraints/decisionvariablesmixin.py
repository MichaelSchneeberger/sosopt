from abc import ABC, abstractmethod

from donotation import do

import statemonad

import polymat
from polymat.typing import MatrixExpression, State

from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol


class DecisionVariablesMixin(ABC):
    @property
    @abstractmethod
    def decision_variable_symbols(self) -> tuple[DecisionVariableSymbol, ...]: ...

    # @property
    # @abstractmethod
    # def anonymous_variable_indices(self) -> tuple[int, ...]: ...


def to_decision_variable_symbols(expr: MatrixExpression):
    def _to_decision_variable_symbols(state: State):
        state, variable_indices = polymat.to_variable_indices(expr).apply(state)

        decision_variable_symbols = []
        # anonymous_variable_indices = []

        for index in variable_indices:
            match state.get_symbol(index=index):
                # case None:
                #     anonymous_variable_indices.append(index)
                case symbol if isinstance(symbol, DecisionVariableSymbol):
                    decision_variable_symbols.append(symbol)

        return state, tuple(set(decision_variable_symbols))
        # return state, (
        #     tuple(decision_variable_symbols),
        #     # tuple(anonymous_variable_indices)
        # )
    return statemonad.get_map_put(_to_decision_variable_symbols)