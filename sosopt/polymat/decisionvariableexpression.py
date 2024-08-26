# from abc import abstractmethod

from polymat.typing import (
    MatrixExpression,
)

# from sosopt.polymat.decisionvariable import DecisionVariable


class DecisionVariableExpression(MatrixExpression):
    """
    Expression that is a polynomial variable, i.e. an expression that cannot be
    reduced further.
    """

    # @property
    # @abstractmethod
    # def variable(self) -> DecisionVariable: ...


class SingleDimDecisionVariableExpression(DecisionVariableExpression):
    pass
