from __future__ import annotations

from abc import abstractmethod
from typing import override
import numpy as np

from donotation import do

import statemonad

import polymat
from polymat.typing import (
    State,
    VectorExpression,
    PolynomialExpression,
    VariableVectorExpression,
)

from sosopt.constraints.constraintprimitives.constraintprimitive import (
    ConstraintPrimitive,
)
from sosopt.constraints.polynomialvariablesmixin import PolynomialVariablesMixin
from sosopt.polymat.abc import PolynomialVariable
from sosopt.polymat.init import init_polynomial_variable
from sosopt.semialgebraicset import SemialgebraicSet
from sosopt.constraints.constraintprimitives.init import (
    init_positive_polynomial_constraint_primitive,
)
from sosopt.constraints.constraint import Constraint


class PutinarsPsatzConstraint(PolynomialVariablesMixin, Constraint):
    # a constraint is a dataclass with information that the user provided, some helper functions,
    # and a function that

    # abstract properties
    #####################

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

    # class method
    ##############

    @property
    @override
    def constraint_primitives(
        self,
    ) -> tuple[ConstraintPrimitive, ...]:
        """create 1 positive polynomial primitive for the condition and for each multiplier"""

        def gen_children():
            for multiplier in self.multipliers.values():
                yield init_positive_polynomial_constraint_primitive(
                    name=self.name,
                    children=tuple(),  # no children
                    condition=multiplier,
                    decision_variable_symbols=(multiplier.coefficients[0][0].symbol,),
                    volatile_symbols=tuple(),
                    polynomial_variables=multiplier.polynomial_variables,
                )

        children = tuple(gen_children())

        def gen_volatile_symbols():
            for multiplier in self.multipliers.values():
                yield multiplier.coefficients[0][0].symbol

        volatile_symbols = tuple(gen_volatile_symbols())

        primitive = init_positive_polynomial_constraint_primitive(
            name=self.name,
            children=children,
            condition=self.sos_polynomial,
            decision_variable_symbols=self.decision_variable_symbols,
            volatile_symbols=volatile_symbols,
            polynomial_variables=self.polynomial_variables,
        )
        return (primitive,)


def get_sos_polynomial(
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


def define_multiplier(
    name: str,
    degree: int,
    multiplicand: VectorExpression,
    variables: VariableVectorExpression,
):
    def round_up_to_even(n):
        if n % 2 == 0:
            return n
        else:
            return n + 1

    max_degree = round_up_to_even(degree)

    @do()
    def create_multiplier():
        multiplicand_degrees = yield from polymat.to_degree(
            multiplicand, variables=variables
        )
        max_degree_multiplicand = int(max(multiplicand_degrees))
        degrees = max_degree - max_degree_multiplicand
        # print(f'{name=}, {max_degree=}, {max_degree_multiplicand=}')
        degree_range = tuple(range(int(degrees) + 1))
        # print(f'{name=}, {degree_range=}')
        expr = init_polynomial_variable(
            name=name,
            monomials=variables.combinations(degree_range).cache(),
            polynomial_variables=variables,
        )
        return statemonad.from_[State](expr)

    return create_multiplier()


def define_multipliers(
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
        # max_degree = yield from polymat.to_degree(condition, variables=variables)
        max_degree = int(np.max(max_degree))

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
