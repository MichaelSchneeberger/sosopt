from __future__ import annotations

from abc import abstractmethod

from statemonad.typing import StateMonad

from polymat.typing import MatrixExpression, State

from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol
from sosopt.coneconstraints.decisionvariablesmixin import DecisionVariablesMixin
from sosopt.coneconstraints.coneconstraint import ConeConstraint


class PolynomialConstraintPrimitive(
    DecisionVariablesMixin,
):
    # abstract properties
    #####################

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def expression(self) -> MatrixExpression: ...

    def copy(self, /, **others) -> PolynomialConstraintPrimitive: ...

    # class method
    ##############

    @abstractmethod
    def to_cone_constraint(
        self, settings: dict
    ) -> StateMonad[State, ConeConstraint]: ...

    def eval(
        self, substitutions: dict[DecisionVariableSymbol, tuple[float, ...]]
    ) -> PolynomialConstraintPrimitive | None:
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
