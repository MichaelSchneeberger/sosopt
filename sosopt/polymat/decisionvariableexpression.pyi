from abc import abstractmethod
from typing import Iterable
from polymat.typing import (
    ExpressionNode,
    VariableExpression,
    SingleValueVariableExpression,
)
from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol

class DecisionVariableExpression(VariableExpression):
    def cache(self) -> DecisionVariableExpression: ...
    def copy(self, child: ExpressionNode) -> DecisionVariableExpression: ...
    @property
    @abstractmethod
    def symbol(self) -> DecisionVariableSymbol: ...
    def iterate_symbols(self) -> Iterable[DecisionVariableSymbol]: ...

class SingleValueDecisionVariableExpression(
    SingleValueVariableExpression, VariableExpression
):
    def cache(self) -> SingleValueDecisionVariableExpression: ...
    def copy(
        self, child: ExpressionNode
    ) -> SingleValueDecisionVariableExpression: ...
