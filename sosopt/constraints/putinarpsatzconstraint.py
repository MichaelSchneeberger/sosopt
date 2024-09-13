from __future__ import annotations

from abc import abstractmethod
from itertools import accumulate
from typing import override
import numpy as np

from donotation import do

import statemonad

import polymat
from polymat.typing import (
    State,
    PolynomialExpression,
    VariableVectorExpression,
)

from sosopt.constraints.constraintprimitives.constraintprimitive import (
    ConstraintPrimitive,
)
from sosopt.constraints.utils.polynomialvariablesmixin import PolynomialVariablesMixin
from sosopt.polymat.from_ import define_multiplier
from sosopt.polymat.polynomialvariable import PolynomialVariable
from sosopt.semialgebraicset import SemialgebraicSet
from sosopt.constraints.constraintprimitives.init import (
    init_sum_of_squares_primitive,
)
from sosopt.constraints.constraint import Constraint


class PutinarsPsatzConstraint(PolynomialVariablesMixin, Constraint):
    # abstract properties

    @property
    @abstractmethod
    def condition(self) -> PolynomialExpression: ...

    @property
    @abstractmethod
    def domain(self) -> SemialgebraicSet: ...

    @property
    @abstractmethod
    def multipliers(self) -> dict[str, PolynomialVariable]:
        """ a dictionary mapping from the name of the equality or inequality constraint to the multiplier """

    @property
    @abstractmethod
    def sos_polynomial(self) -> PolynomialExpression: ...

    # methods

    @override
    def get_constraint_primitives(
        self,
    ) -> tuple[ConstraintPrimitive, ...]:
        
        def gen_children():
            """Create an SOS constraint primitive for each inequality"""

            for name in self.domain.inequalities.keys():

                multiplier = self.multipliers[name]

                yield init_sum_of_squares_primitive(
                    name=self.name,
                    children=tuple(),  # no children
                    condition=multiplier,
                    decision_variable_symbols=(multiplier.coefficients[0][0].symbol,),
                    polynomial_variables=multiplier.polynomial_variables,
                )

        children = tuple(gen_children())

        primitive = init_sum_of_squares_primitive(
            name=self.name,
            children=children,
            condition=self.sos_polynomial,
            decision_variable_symbols=self.decision_variable_symbols,
            polynomial_variables=self.polynomial_variables,
        )

        return (primitive,)


def define_putinars_psatz_condition(
    condition: PolynomialExpression,
    domain: SemialgebraicSet,
    multipliers: dict[str, PolynomialVariable],
) -> PolynomialExpression:
    constraints = domain.inequalities | domain.equalities

    def acc_domain_polynomials(acc, next):
        domain_name, constraint = next

        return acc - multipliers[domain_name] * constraint
        
    *_, n_condition = accumulate(
        constraints.items(),
        acc_domain_polynomials,
        initial=condition,
    )

    return n_condition


def define_psatz_multipliers(
    name: str,
    condition: PolynomialExpression,
    domain: SemialgebraicSet,
    variables: VariableVectorExpression,
):
    @do()
    def create_multipliers():
        constraints = domain.inequalities | domain.equalities

        def gen_vector():
            yield condition

            if domain is not None:
                yield from domain.inequalities.values()
                yield from domain.equalities.values()

        vector = polymat.v_stack(gen_vector()).to_vector()
        max_degree = yield from polymat.to_degree(vector, variables=variables)
        max_degree = max(max(max_degree))

        def gen_multipliers():
            for constraint_name, constraint_expr in constraints.items():

                @do()
                def create_multiplier(constraint_expr=constraint_expr):
                    expr = yield from define_multiplier(
                        name=f"{name}_{constraint_name}_gamma",
                        degree=max_degree,
                        multiplicand=constraint_expr,
                        variables=variables,
                    )

                    return statemonad.from_[State]((constraint_name, expr))

                yield create_multiplier()

        multipliers = yield from statemonad.zip(gen_multipliers())

        return statemonad.from_[State](dict(multipliers))

    return create_multipliers()
