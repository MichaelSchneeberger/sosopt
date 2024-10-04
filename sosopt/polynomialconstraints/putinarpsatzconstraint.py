from __future__ import annotations

from dataclasses import replace

from dataclassabc import dataclassabc

from sosopt.polynomialconstraints.constraintprimitive.sumofsquaresprimitive import init_sum_of_squares_primitive
import statemonad

import polymat
from polymat.typing import (
    State,
    VariableVectorExpression,
    MatrixExpression,
    PolynomialExpression,
)

from sosopt.polynomialconstraints.constraintprimitive.constraintprimitive import (
    ConstraintPrimitive,
)
from sosopt.utils.decisionvariablesmixin import to_decision_variable_symbols
from sosopt.utils.polynomialvariablesmixin import (
    PolynomialVariablesMixin,
    to_polynomial_variables,
)
from sosopt.polymat.from_ import define_multiplier
from sosopt.polymat.polynomialvariable import PolynomialVariable
from sosopt.semialgebraicset import SemialgebraicSet
from sosopt.polynomialconstraints.polynomialconstraint import PolynomialConstraint


@dataclassabc(frozen=True, slots=True)
class PutinarPsatzConstraint(PolynomialVariablesMixin, PolynomialConstraint):
    name: str
    condition: MatrixExpression
    shape: tuple[int, int]
    domain: SemialgebraicSet
    multipliers: dict[tuple[int, int], dict[str, PolynomialVariable]]
    sos_polynomials: dict[tuple[int, int], PolynomialExpression]
    polynomial_variables: VariableVectorExpression
    primitives: tuple[ConstraintPrimitive, ...]

    def copy(self, /, **others):
        return replace(self, **others)


def init_putinar_psatz_constraint(
    name: str,
    condition: MatrixExpression,
    domain: SemialgebraicSet,
):
    def create_constraint(state: State):
        state, polynomial_variables = to_polynomial_variables(condition).apply(state)

        domain_polynomials = domain.inequalities | domain.equalities

        vector = polymat.v_stack(domain_polynomials.values()).to_vector()
        state, max_domain_degrees = polymat.to_degree(
            vector, variables=polynomial_variables
        ).apply(state)
        max_domain_degree = max(max(max_domain_degrees))

        state, (n_rows, n_cols) = polymat.to_shape(condition).apply(state)

        multipliers = {}
        sos_polynomials = {}
        constraint_primitives = []

        for row in range(n_rows):
            for col in range(n_cols):
                condition_entry = condition[row, col]

                state, max_cond_degrees = polymat.to_degree(
                    condition_entry,
                    variables=polynomial_variables,
                ).apply(state)
                max_cond_degree = max(max(max_cond_degrees))
                
                sos_polynomial_entry = condition_entry
                multipliers_entry = {}

                for domain_name, domain_polynomial in domain_polynomials.items():
                    state, multiplier = define_multiplier(
                        name=f"{name}_{row}_{col}_{domain_name}",
                        degree=max(max_domain_degree, max_cond_degree),
                        multiplicand=domain_polynomial,
                        variables=polynomial_variables,
                    ).apply(state)

                    multipliers_entry[domain_name] = multiplier

                    sos_polynomial_entry = sos_polynomial_entry - multiplier * domain_polynomial

                    constraint_primitives.append(
                        init_sum_of_squares_primitive(
                            name=name,
                            expression=multiplier,
                            decision_variable_symbols=tuple(multiplier.iterate_symbols()),
                            polynomial_variables=polynomial_variables,
                        )
                    )

                multipliers[row, col] = multipliers_entry
                sos_polynomials[row, col] = sos_polynomial_entry

                state, decision_variables = to_decision_variable_symbols(
                    sos_polynomial_entry
                ).apply(state)

                constraint_primitives.append(
                    init_sum_of_squares_primitive(
                        name=name,
                        expression=sos_polynomial_entry,
                        decision_variable_symbols=decision_variables,
                        polynomial_variables=polynomial_variables,
                    )
                )

        constraint = PutinarPsatzConstraint(
            name=name,
            condition=condition,
            shape=(n_rows, n_cols),
            polynomial_variables=polynomial_variables,
            domain=domain,
            multipliers=multipliers,
            sos_polynomials=sos_polynomials,
            primitives=tuple(constraint_primitives),
        )
        return state, constraint
    
    return statemonad.get_map_put(create_constraint)
