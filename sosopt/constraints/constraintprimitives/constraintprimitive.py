from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterator

from polymat.typing import MatrixExpression, VectorExpression

from sosopt.constraints.decisionvariablesmixin import DecisionVariablesMixin
from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol


class ConstraintPrimitive(DecisionVariablesMixin):
    # abstract properties
    #####################

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def children(self) -> tuple[ConstraintPrimitive, ...]: ...

    @property
    @abstractmethod
    def condition(self) -> MatrixExpression: ...

    @property
    @abstractmethod
    def volatile_symbols(self) -> tuple[DecisionVariableSymbol, ...]: ...

    def copy(self, /, **others) -> ConstraintPrimitive: ...

    # class method
    ##############

    def flatten(self) -> Iterator[ConstraintPrimitive]:
        yield self
        yield from self.children

    # @abstractmethod
    def eval(
        self, substitutions: dict[DecisionVariableSymbol, tuple[float, ...]]
    ) -> ConstraintPrimitive | None:
        
        def not_in_substitutions(p: DecisionVariableSymbol):
            return p not in substitutions

        # find symbols that are not getting substituted
        decision_variable_symbols = tuple(filter(not_in_substitutions, self.decision_variable_symbols))
        # print(f'{self.name=}, {self.decision_variable_symbols=}, {decision_variable_symbols=}')

        def not_volatile(p: DecisionVariableSymbol):
            return p not in self.volatile_symbols
        
        non_volatile = tuple(filter(not_volatile, decision_variable_symbols))

        # remove constraint primitive if not depending on decision variables
        if len(non_volatile) != 0:
            condition = self.condition.eval(substitutions)

            def gen_children():
                for child in self.children:
                    eval_child = child.eval(substitutions)
                    if eval_child is not None:
                        yield eval_child

            return self.copy(
                condition=condition,
                decision_variable_symbols=decision_variable_symbols,
                children=tuple(gen_children()),
            )

    @abstractmethod
    def to_constraint_vector() -> VectorExpression: ...
