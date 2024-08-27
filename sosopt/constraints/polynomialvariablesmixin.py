from abc import ABC, abstractmethod

from donotation import do

import statemonad
from statemonad.typing import StateMonad

import polymat
from polymat.typing import (
    State,
    PolynomialExpression,
    VariableVectorExpression,
)

from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol


class PolynomialVariablesMixin(ABC):
    @property
    @abstractmethod
    def polynomial_variables(self) -> VariableVectorExpression: ...


def to_polynomial_variables(
    condition: PolynomialExpression,
) -> StateMonad[State, VariableVectorExpression]:
    """ Assume everything that is not a decision variable to be a polynomial variable """

    @do()
    def _to_polynomial_variables():

        # get indices in the same order as they appear in the variable vector
        variable_indices = yield from polymat.to_variable_indices(condition.to_variable_vector())

        state = yield from statemonad.get[State]()

        def gen_polynomial_indices():
            for index in variable_indices:
                symbol = state.get_symbol(index=index)

                if not isinstance(symbol, DecisionVariableSymbol):
                    yield index

        polynomial_indices = tuple(gen_polynomial_indices())

        vector = polymat.from_variable_indices(polynomial_indices).cache()

        # value = yield from polymat.to_sympy(vector)
        # print(f'{value=}')

        return statemonad.from_[State](vector)

    return _to_polynomial_variables()
