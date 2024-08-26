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


def to_decision_variable_symbols(expr: MatrixExpression):
    @do()
    def _to_decision_variable_symbols():
        variables = yield from polymat.to_variables(expr)

        def gen_decision_variable_symbols():
            for variable in variables:
                if isinstance(variable, DecisionVariableSymbol):
                    yield variable

        decision_variable_symbols = tuple(gen_decision_variable_symbols())

        return statemonad.from_[State](decision_variable_symbols)

    return _to_decision_variable_symbols()
