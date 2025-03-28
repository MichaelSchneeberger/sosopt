from abc import abstractmethod

from polymat.state.state import State as PolyMatState
from polymat.sparserepr.data.polynomial import PolynomialType


class State(PolyMatState):
    @property
    @abstractmethod
    def auxilliary_equations(self) -> tuple[PolynomialType, ...]:
        ...

    @property
    @abstractmethod
    def sparse_smr(self) -> bool:
        ...
