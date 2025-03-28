from abc import ABC, abstractmethod
from functools import cached_property

import statemonad
from statemonad.typing import StateMonad

import polymat
from polymat.typing import (
    StrSymbol,
    State as BaseState,
    MatrixExpression,
)


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
            condition
        ).apply(state)

        def gen_polynomial_indices():
            for index in variable_indices:
                match state.get_symbol(index=index):
                    case StrSymbol():
                        yield index

        return state, tuple(set(gen_polynomial_indices()))

    return statemonad.get_map_put(_to_polynomial_variables)
