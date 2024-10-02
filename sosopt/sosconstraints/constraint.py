from __future__ import annotations

from abc import abstractmethod

from statemonad.typing import StateMonad

from polymat.typing import State

from sosopt.coneconstraints.coneconstraint import (
    ConeConstraint,
)
from sosopt.utils.decisionvariablesmixin import DecisionVariablesMixin


class Constraint(DecisionVariablesMixin):
    """
    A constraints implements helper methods that can be used to define the cost function
    """

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def get_cone_constraints(
        self,
    ) -> tuple[ConeConstraint, ...]:
        """
        Generates a tree of cone constraint, encoding the dependency between constraints.
        """
