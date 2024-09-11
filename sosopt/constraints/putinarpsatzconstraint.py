from __future__ import annotations

from abc import abstractmethod
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
    init_positive_polynomial_primitive,
)
from sosopt.constraints.constraint import Constraint


class PutinarsPsatzConstraint(PolynomialVariablesMixin, Constraint):
    # abstract properties

    @property
    @abstractmethod
    def condition(self) -> PolynomialExpression: ...

    @property
    @abstractmethod
    def domain(self) -> SemialgebraicSet | None: ...

    @property
    @abstractmethod
    def multipliers(self) -> dict[str, PolynomialVariable]: ...

    @property
    @abstractmethod
    def sos_polynomial(self) -> PolynomialExpression: ...

    """ a dictionary mapping from the name of the equality or inequality constraint to the multiplier """

    # methods

    @override
    def get_constraint_primitives(
        self,
    ) -> tuple[ConstraintPrimitive, ...]:
        """create 1 positive polynomial primitive for the condition and for each multiplier"""

        def gen_children():
            for multiplier in self.multipliers.values():
                yield init_positive_polynomial_primitive(
                    name=self.name,
                    children=tuple(),  # no children
                    condition=multiplier,
                    decision_variable_symbols=(multiplier.coefficients[0][0].symbol,),
                    polynomial_variables=multiplier.polynomial_variables,
                )

        children = tuple(gen_children())

        primitive = init_positive_polynomial_primitive(
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
    condition = condition

    constraints = domain.inequalities | domain.equalities
    for domain_name in constraints.keys():
        multiplier = multipliers[domain_name]
        condition = condition - multiplier * constraints[domain_name]

    return condition


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
                def create_multiplier():
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
