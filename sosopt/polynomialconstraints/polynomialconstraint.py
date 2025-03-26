from __future__ import annotations

from abc import abstractmethod

from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol
from sosopt.polynomialconstraints.constraintprimitives.polynomialconstraintprimitive import (
    PolynomialConstraintPrimitive,
)


class PolynomialConstraint:
    """
    A constraints implements helper methods that can be used to define the cost function
    """

    @property
    @abstractmethod
    def name(self) -> str: ...

    def copy(self, /, **others) -> PolynomialConstraint: ...

    @property
    @abstractmethod
    def primitives(self) -> tuple[PolynomialConstraintPrimitive, ...]: ...

    def eval(
        self, 
        substitutions: dict[DecisionVariableSymbol, tuple[float, ...]]
    ) -> PolynomialConstraint | None:
        def gen_evaluated_primitives():
            for primitive in self.primitives:
                evaluated_primitive = primitive.eval(substitutions)

                # primitive contains decision variables after evaluation
                if evaluated_primitive is not None:
                    yield evaluated_primitive

        evaluated_primitives = tuple(gen_evaluated_primitives())
        return self.copy(primitives=evaluated_primitives)
