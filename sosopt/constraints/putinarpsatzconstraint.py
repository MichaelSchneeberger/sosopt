from __future__ import annotations

from abc import abstractmethod
from collections import defaultdict
from itertools import accumulate
from typing import override

from donotation import do

import statemonad

import polymat
from polymat.typing import (
    State,
    PolynomialExpression,
    VariableVectorExpression,
    MatrixExpression,
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
    #####################

    @property
    @abstractmethod
    def condition(self) -> MatrixExpression: ...

    @property
    @abstractmethod
    def domain(self) -> SemialgebraicSet: ...

    @property
    @abstractmethod
    def multipliers(self) -> dict[tuple[int, int], dict[str, PolynomialVariable]]:
        """ a dictionary mapping from the name of the equality or inequality constraint to the multiplier """

    @property
    @abstractmethod
    def sos_polynomial(self) -> MatrixExpression: ...

    @property
    @abstractmethod
    def shape(self) -> tuple[int, int]: ...

    # methods
    #########

    @override
    def get_constraint_primitives(
        self,
    ) -> tuple[ConstraintPrimitive, ...]:
        
        n_rows, n_cols = self.shape
        
        def gen_primitives():
            for row in range(n_rows):
                for col in range(n_cols):
                    multiplier_entry = self.multipliers[row, col]

                    def gen_children():
                        """Create an SOS constraint primitive for each inequality"""

                        for name in self.domain.inequalities.keys():

                            multiplier = multiplier_entry[name]

                            yield init_sum_of_squares_primitive(
                                name=self.name,
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
                    yield primitive

        return tuple(gen_primitives())


def define_putinars_psatz_condition(
    condition: MatrixExpression,
    domain: SemialgebraicSet,
    multipliers: dict[tuple[int, int], dict[str, PolynomialVariable]],
    shape: tuple[int, int],
) -> MatrixExpression:
    constraints = domain.inequalities | domain.equalities

    n_rows, n_cols = shape

    def gen_rows():
        for row in range(n_rows):
            def gen_cols():
                for col in range(n_cols):
                    multipliers_entry = multipliers[row, col]

                    def acc_domain_polynomials(acc, next):
                        domain_name, constraint = next

                        return acc - multipliers_entry[domain_name] * constraint
                        
                    *_, condition_entry = accumulate(
                        constraints.items(),
                        acc_domain_polynomials,
                        initial=condition[row, col],
                    )

                    yield condition_entry
            
            cols = tuple(gen_cols())

            if 1 < len(cols):
                result = polymat.h_stack(cols)
            else:
                result = cols[0]
            yield result

    rows = tuple(gen_rows())

    if 1 < len(rows):
        result = polymat.v_stack(rows)
    else:
        result = rows[0]
    return result


def define_psatz_multipliers(
    name: str,
    condition: MatrixExpression,
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
        max_degrees = yield from polymat.to_degree(vector, variables=variables)
        max_degree = max(max(max_degrees))

        n_rows, n_cols = yield from polymat.to_shape(condition)

        def gen_multipliers():
            for row in range(n_rows):
                for col in range(n_cols):
                    for constraint_name, constraint_expr in constraints.items():

                        @do()
                        def create_multiplier(constraint_expr=constraint_expr):
                            expr = yield from define_multiplier(
                                name=f"{name}_{constraint_name}_gamma",
                                degree=max_degree,
                                multiplicand=constraint_expr,
                                variables=variables,
                            )

                            entry = (row, col), constraint_name, expr

                            return statemonad.from_[State](entry)

                        yield create_multiplier()

        multipliers = yield from statemonad.zip(gen_multipliers())

        def convert_to_dict():
            multipliers_dict = defaultdict(dict)
            for index, name, expr in multipliers:
                multipliers_dict[index][name] = expr
            return multipliers_dict

        return statemonad.from_[State](convert_to_dict())

    return create_multipliers()
