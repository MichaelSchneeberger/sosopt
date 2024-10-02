from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterator

from polymat.typing import MatrixExpression, VectorExpression

from sosopt.utils.decisionvariablesmixin import DecisionVariablesMixin
from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol


class ConeConstraint(DecisionVariablesMixin):
    # abstract properties
    #####################

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def children(self) -> tuple[ConeConstraint, ...]: ...       # remove?

    @property
    @abstractmethod
    def condition(self) -> MatrixExpression: ...

    def copy(self, /, **others) -> ConeConstraint: ...

    # class method
    ##############

    def flatten(self) -> Iterator[ConeConstraint]:
        yield self
        yield from self.children

    def eval(
        self, substitutions: dict[DecisionVariableSymbol, tuple[float, ...]]
    ) -> ConeConstraint | None:
        def not_in_substitutions(p: DecisionVariableSymbol):
            return p not in substitutions

        # find symbols that are not getting substituted
        decision_variable_symbols = tuple(
            filter(not_in_substitutions, self.decision_variable_symbols)
        )

        if len(decision_variable_symbols):
            condition = self.condition.eval(substitutions)

            # remove cone constraints if not depending on decision variables
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


class EqualityConstraint(ConeConstraint): ...
class LinearConstraint(ConeConstraint): ...
class QuadraticConeConstraint(ConeConstraint): ...
class SDPConstraint(ConeConstraint): ...
