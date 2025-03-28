from abc import abstractmethod
from typing import Iterable
from polymat.typing import (
    State as BaseState,
    ExpressionNode,
    VariableExpression,
    VariableVectorExpression,
)

# from sosopt.state.state import State as BaseState
from sosopt.polymat.symbols.decisionvariablesymbol import DecisionVariableSymbol

class DecisionVariableVectorSymbolExpression[State: BaseState](
    VariableVectorExpression
):
    def cache(self) -> DecisionVariableVectorSymbolExpression[State]: ...
    def copy(
        self, child: ExpressionNode
    ) -> DecisionVariableVectorSymbolExpression[State]: ...
    @property
    @abstractmethod
    def symbol(self) -> DecisionVariableSymbol: ...
    def iterate_symbols(self) -> Iterable[DecisionVariableSymbol]: ...

class DecisionVariableExpression[State: BaseState](
    VariableExpression,
    DecisionVariableVectorSymbolExpression
):
    def cache(self) -> DecisionVariableExpression[State]: ...
    def copy(self, child: ExpressionNode) -> DecisionVariableExpression[State]: ...
