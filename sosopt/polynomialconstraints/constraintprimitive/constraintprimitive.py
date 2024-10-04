from __future__ import annotations

from abc import abstractmethod

from polymat.typing import MatrixExpression

from sosopt.coneconstraints.coneconstraint import ConeConstraint
from sosopt.utils.decisionvariablesmixin import DecisionVariablesMixin
from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol


class ConstraintPrimitive(DecisionVariablesMixin):
    # abstract properties
    #####################

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def expression(self) -> MatrixExpression: ...

    def copy(self, /, **others) -> ConstraintPrimitive: ...

    # class method
    ##############

    @abstractmethod
    def to_cone_constraint(self) -> ConeConstraint: ...

    def eval(
        self, substitutions: dict[DecisionVariableSymbol, tuple[float, ...]]
    ) -> ConstraintPrimitive | None:
        def not_in_substitutions(p: DecisionVariableSymbol):
            return p not in substitutions

        # find symbols that are not getting substituted
        decision_variable_symbols = tuple(
            filter(not_in_substitutions, self.decision_variable_symbols)
        )

        if len(decision_variable_symbols):
            evaluated_expression = self.expression.eval(substitutions)

            return self.copy(
                expression=evaluated_expression,
                decision_variable_symbols=decision_variable_symbols,
            )
