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
    VariableVectorExpression,
    MatrixExpression,
)

from sosopt.coneconstraints.coneconstraint import (
    ConeConstraint,
)
from sosopt.utils.polynomialvariablesmixin import PolynomialVariablesMixin
from sosopt.polymat.from_ import define_multiplier
from sosopt.polymat.polynomialvariable import PolynomialVariable
from sosopt.semialgebraicset import SemialgebraicSet
from sosopt.coneconstraints.init import (
    init_sum_of_squares_constraint,
)
from sosopt.polynomialconstraints.polynomialconstraint import PolynomialConstraint


class PutinarsPsatzConstraint(PolynomialVariablesMixin, PolynomialConstraint):

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
    def get_cone_constraints(
        self,
    ) -> tuple[ConeConstraint, ...]:
        
        n_rows, n_cols = self.shape
        
        def gen_cone_constraints():
            for row in range(n_rows):
                for col in range(n_cols):
                    multiplier_entry = self.multipliers[row, col]

                    # def gen_children():
                    #     """Create a cone constraint for each inequality"""

                    for name in self.domain.inequalities.keys():

                        multiplier = multiplier_entry[name]

                        yield init_sum_of_squares_constraint(
                            name=self.name,
                            condition=multiplier,
                            decision_variable_symbols=(multiplier.coefficients[0][0].symbol,),
                            polynomial_variables=multiplier.polynomial_variables,
                        )

                    # children = tuple(gen_children())
                    # yield from children

                    constraint = init_sum_of_squares_constraint(
                        name=self.name,
                        # children=children,
                        condition=self.sos_polynomial[row, col],
                        decision_variable_symbols=self.decision_variable_symbols,
                        polynomial_variables=self.polynomial_variables,
                    )
                    yield constraint

        return tuple(gen_cone_constraints())


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
        domain_polynomials = domain.inequalities | domain.equalities

        vector = polymat.v_stack(domain_polynomials.values()).to_vector()
        max_domain_degrees = yield from polymat.to_degree(vector, variables=variables)
        max_domain_degree = max(max(max_domain_degrees))

        n_rows, n_cols = yield from polymat.to_shape(condition)

        def gen_multipliers():
            for row in range(n_rows):
                for col in range(n_cols):

                    for domain_name, domain_polynomial in domain_polynomials.items():

                        @do()
                        def create_multiplier(constraint_expr=domain_polynomial):

                            max_cond_degrees = yield from polymat.to_degree(condition[row, col], variables=variables)
                            max_cond_degree = max(max(max_cond_degrees))

                            expr = yield from define_multiplier(
                                name=f"{name}_{row}_{col}_{domain_name}",
                                degree=max(max_domain_degree, max_cond_degree),
                                multiplicand=constraint_expr,
                                variables=variables,
                            )

                            entry = (row, col), domain_name, expr

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
