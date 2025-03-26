from abc import ABC, abstractmethod
from functools import cached_property

import statemonad
from statemonad.typing import StateMonad

import polymat
from polymat.typing import (
    State as BaseState,
    MatrixExpression,
)

from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol


class PolynomialVariablesMixin(ABC):
    @property
    @abstractmethod
    def polynomial_variable_indices(self) -> tuple[int, ...]: ...

    @cached_property
    def polynomial_variable(self):
        return polymat.from_variable_indices(
            self.polynomial_variable_indices,
        ).cache()


def to_polynomial_variable_indices[State: BaseState](
    condition: MatrixExpression[State],
) -> StateMonad[State, tuple[int, ...]]:
    """Assume everything that is not a decision variable to be a polynomial variable"""

    def _to_polynomial_variables(state: State):

        # get indices in the same order as they appear in the variable vector
        state, variable_indices = polymat.to_variable_indices(
            # condition.to_variable_vector()
            condition
        ).apply(state)

        # state = yield from statemonad.get[State]()

        def gen_polynomial_indices():
            for index in variable_indices:
                symbol = state.get_symbol(index=index)

                if not isinstance(symbol, DecisionVariableSymbol):
                    yield index

        indices = tuple(gen_polynomial_indices())

        # vector = polymat.from_variable_indices(polynomial_indices).cache()

        return state, indices

    return statemonad.get_map_put(_to_polynomial_variables)
