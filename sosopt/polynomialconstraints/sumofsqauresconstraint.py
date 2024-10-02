from __future__ import annotations
from abc import abstractmethod
from typing import override

from polymat.typing import MatrixExpression

from sosopt.polynomialconstraints.polynomialconstraint import PolynomialConstraint
from sosopt.coneconstraints.coneconstraint import (
    ConeConstraint,
)
from sosopt.coneconstraints.init import (
    init_sum_of_squares_constraint,
)
from sosopt.utils.polynomialvariablesmixin import PolynomialVariablesMixin


class SumOfSqauresConstraint(PolynomialVariablesMixin, PolynomialConstraint):
    @property
    @abstractmethod
    def condition(self) -> MatrixExpression: ...

    @property
    @abstractmethod
    def shape(self) -> tuple[int, int]: ...

    @override
    def get_cone_constraints(
        self,
    ) -> tuple[ConeConstraint, ...]:
        
        def gen_cone_constraints():
            n_rows, n_cols = self.shape
            for row in range(n_rows):
                for col in range(n_cols):
                    yield init_sum_of_squares_constraint(
                        name=self.name,
                        condition=self.condition[row, col],
                        decision_variable_symbols=self.decision_variable_symbols,
                        polynomial_variables=self.polynomial_variables,
                    )
                    
        return tuple(gen_cone_constraints())
