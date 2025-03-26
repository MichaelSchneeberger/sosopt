from __future__ import annotations

from abc import abstractmethod

from polymat.typing import MatrixExpression, VectorExpression
from sosopt.coneconstraints.anonymousvariablesmixin import AnonymousVariablesMixin
from sosopt.coneconstraints.decisionvariablesmixin import DecisionVariablesMixin
from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol


class ConeConstraint(AnonymousVariablesMixin, DecisionVariablesMixin):
    # abstract properties
    #####################

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def expression(self) -> MatrixExpression: ...

    # @property
    # @abstractmethod
    # def anonymous_variable_indices(self) -> tuple[int, ...]:
    #     ...

    # abstract methods
    ##################

    @abstractmethod
    def copy(self, /, **others) -> ConeConstraint: ...

    def eval(
        self, 
        substitutions: dict[DecisionVariableSymbol, tuple[float, ...]]
    ) -> ConeConstraint | None:
        # find variable symbols that is not getting substitued
        decision_variable_symbols = tuple(
            symbol
            for symbol in self.decision_variable_symbols
            if symbol not in substitutions
        )

        if len(decision_variable_symbols):
            evaluated_expression = self.expression.eval(substitutions)

            return self.copy(
                expression=evaluated_expression,
                decision_variable_symbols=decision_variable_symbols,
            )

    @abstractmethod
    def to_vector(self) -> VectorExpression: ...
