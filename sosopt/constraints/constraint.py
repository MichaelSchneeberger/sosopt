from __future__ import annotations

from abc import abstractmethod

from sosopt.constraints.constraintprimitives.constraintprimitive import (
    ConstraintPrimitive,
)
from sosopt.constraints.utils.decisionvariablesmixin import DecisionVariablesMixin


class Constraint(DecisionVariablesMixin):
    """
    A constraints implements helper methods that can be used to define the cost function
    """

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def constraint_primitives(
        self,
    ) -> tuple[ConstraintPrimitive, ...]:
        """
        Generates a tree of constraint primitives, encoding the dependency between constraints

        primitives are closer to what the solver can solve
        """
