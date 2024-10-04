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


@do()
def to_decision_variable_symbols(expr: MatrixExpression):
    variable_indices = yield from polymat.to_variable_indices(expr)

    state = yield from statemonad.get[State]()

    def gen_polynomial_indices():
        for index in variable_indices:
            yield state.get_symbol(index=index)

    symbols = tuple(set(gen_polynomial_indices()))

    def gen_decision_variable_symbols():
        for symbol in symbols:
            if isinstance(symbol, DecisionVariableSymbol):
                yield symbol

    decision_variable_symbols = tuple(gen_decision_variable_symbols())

    return statemonad.from_[State](decision_variable_symbols)
