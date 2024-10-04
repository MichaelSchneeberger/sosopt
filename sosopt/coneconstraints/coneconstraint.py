from __future__ import annotations

from abc import abstractmethod

from polymat.typing import MatrixExpression, VectorExpression
from sosopt.utils.decisionvariablesmixin import DecisionVariablesMixin


class ConeConstraint(DecisionVariablesMixin):
    # abstract properties
    #####################

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def expression(self) -> MatrixExpression: ...

    # abstract methods
    ##################

    @abstractmethod
    def copy(self, /, **others) -> ConeConstraint: ...

    @abstractmethod
    def to_vector(self) -> VectorExpression: ...
