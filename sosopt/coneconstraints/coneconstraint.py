from __future__ import annotations

from abc import abstractmethod

import statemonad

import polymat
from polymat.typing import MatrixExpression, VectorExpression, State

# from sosopt.coneconstraints.anonymousvariablesmixin import AnonymousVariablesMixin
# from sosopt.coneconstraints.decisionvariablesmixin import DecisionVariablesMixin
from sosopt.polymat.symbols.conedecisionvariablesymbol import ConeDecisionVariableSymbol
# from sosopt.polymat.symbols.decisionvariablesymbol import DecisionVariableSymbol


class ConeConstraint:
    # abstract properties
    #####################

    # @property
    # @abstractmethod
    # def name(self) -> str: ...

    @property
    @abstractmethod
    def expression(self) -> MatrixExpression: ...

    @property
    @abstractmethod
    def decision_variable_symbols(self) -> tuple[ConeDecisionVariableSymbol, ...]:
        ...

    # abstract methods
    ##################

    @abstractmethod
    def copy(self, /, **others) -> ConeConstraint: ...

    def eval(
        self, 
        substitutions: dict[ConeDecisionVariableSymbol, tuple[float, ...]]
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


def to_decision_variable_symbols(expr: MatrixExpression):
    def _to_decision_variable_symbols(state: State):
        state, variable_indices = polymat.to_variable_indices(expr).apply(state)

        def gen_decision_variable_symbol():
            for index in variable_indices:
                match symbol := state.get_symbol(index=index):
                    case ConeDecisionVariableSymbol():
                        yield symbol

        return state, tuple(set(gen_decision_variable_symbol()))

    return statemonad.get_map_put(_to_decision_variable_symbols)
