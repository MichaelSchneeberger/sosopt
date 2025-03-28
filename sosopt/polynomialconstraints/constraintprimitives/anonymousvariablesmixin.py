from abc import ABC, abstractmethod

from sosopt.polymat.symbols.auxiliaryvariablesymbol import AuxiliaryVariableSymbol
import statemonad

import polymat
from polymat.typing import MatrixExpression, State


class AnonymousVariablesMixin(ABC):
    @property
    @abstractmethod
    def anonymous_variable_indices(self) -> tuple[int, ...]: ...



def to_anonymous_variable_indices(
    expression: MatrixExpression,
):
    def _to_anonymous_variable_indices(state: State):
        state, variable_indices = polymat.to_variable_indices(expression).apply(state)

        def gen_anonymous_variable_indices():
            for index in variable_indices:

                match state.get_symbol(index=index):
                    case AuxiliaryVariableSymbol():
                        yield index

        return state, tuple(gen_anonymous_variable_indices())
    
    return statemonad.get_map_put(_to_anonymous_variable_indices)
