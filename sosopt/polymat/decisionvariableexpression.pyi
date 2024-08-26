from abc import abstractmethod
from polymat.typing import (
    ExpressionTreeMixin,
    VariableExpression,
    SingleDimVariableExpression,
)
from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol

class DecisionVariableExpression(VariableExpression):
    def cache(self) -> DecisionVariableExpression: ...
    def copy(
        self, child: ExpressionTreeMixin
    ) -> DecisionVariableExpression: ...

    @property
    @abstractmethod
    def symbol(self) -> DecisionVariableSymbol: ...

class SingleDimDecisionVariableExpression(
    SingleDimVariableExpression, VariableExpression
):
    def cache(self) -> SingleDimDecisionVariableExpression: ...
    def copy(self, child: ExpressionTreeMixin) -> SingleDimDecisionVariableExpression: ...
