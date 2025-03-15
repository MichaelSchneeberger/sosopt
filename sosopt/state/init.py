from dataclasses import replace
from typing import override
from dataclassabc import dataclassabc

from polymat.symbol import Symbol
from polymat.sparserepr.data.polynomial import PolynomialType

from sosopt.state.state import State


@dataclassabc(frozen=True, slots=True)
class StateImpl(State):
    n_indices: int

    """
    Map from variables to two indices defining the index range.
    """
    indices: dict[Symbol, tuple[int, int]]

    """
    Used to cache the computed sparse representation of an expressions so that
    it does not need to be recomputed again.
    """
    cache: dict

    auxilliary_equations: tuple[PolynomialType, ...]

    @override
    def copy(self, /, **changes):
        return replace(self, **changes)


def init_state():
    return StateImpl(
        n_indices=0,
        indices={},
        cache={},
        auxilliary_equations=tuple(),
    )