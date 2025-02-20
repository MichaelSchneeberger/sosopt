from __future__ import annotations

from dataclasses import replace

from dataclassabc import dataclassabc

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
from sosopt.polynomialconstraints.constraintprimitive.sumofsquaresprimitive import init_sum_of_squares_primitive


@dataclassabc(frozen=True, slots=True)
class PutinarPsatzConstraint(PolynomialVariablesMixin, PolynomialConstraint):
    name: str                                                           # override
    primitives: tuple[ConstraintPrimitive, ...]                         # override
    polynomial_variables: VariableVectorExpression                      # override

    # the parametrized polynomial matrix that is rquired to be positive in each entry on the domain
    positive_matrix: MatrixExpression

    # shape of the polynomial matrix
    shape: tuple[int, int]

    # domain defined by the intersection of zero-sublevel sets of a set of polynomials
    domain: SemialgebraicSet | None
    
    # multipliers used to build the SOS certificate for each entry in the matrix
    multipliers: dict[tuple[int, int], dict[str, PolynomialVariable]]

    # SOS certificate required to prove the non-negativity of the target polynomials 
    # (for each entry in the matrix) over the domain
    sos_certificates: dict[tuple[int, int], PolynomialExpression]

    def copy(self, /, **others):
        return replace(self, **others)


def init_putinar_psatz_constraint(
    name: str,
    positive_matrix: MatrixExpression,
    domain: SemialgebraicSet | None = None,
):

    def create_constraint(state: State):

        if domain is None:
            inequalities = {}
            equalities = {}
        
        else:
            inequalities = domain.inequalities
            equalities = domain.equalities

        domain_polynomials = inequalities | equalities

        vector = polymat.v_stack(domain_polynomials.values()).to_vector()

        state, polynomial_variables = to_polynomial_variables(vector).apply(state)

        state, max_domain_degrees = polymat.to_degree(
            vector, variables=polynomial_variables
        ).apply(state)
        max_domain_degree = max(max(max_domain_degrees))

        state, shape = polymat.to_shape(positive_matrix).apply(state)
        n_rows, n_cols = shape

        multipliers = {}
        sos_certificates = {}
        constraint_primitives = []

        match shape:
            case (1, 1):
                get_name = lambda r, c, d: f"{name}_{d}"  # noqa: E731
            case (1, _):
                get_name = lambda r, c, d: f"{name}_{c}_{d}"  # noqa: E731
            case (_, 1):
                get_name = lambda r, c, d: f"{name}_{r}_{d}"  # noqa: E731
            case _:
                get_name = lambda r, c, d: f"{name}_{r}_{c}_{d}"  # noqa: E731

        for row in range(n_rows):
            for col in range(n_cols):
                condition_entry = positive_matrix[row, col]

                state, max_cond_degrees = polymat.to_degree(
                    condition_entry,
                    variables=polynomial_variables,
                ).apply(state)
                max_cond_degree = max(max(max_cond_degrees))
                
                sos_polynomial_entry = condition_entry
                multipliers_entry = {}

                for domain_name, domain_polynomial in domain_polynomials.items():
                    state, multiplier = define_multiplier(
                        name=get_name(row, col, domain_name),
                        degree=max(max_domain_degree, max_cond_degree),
                        multiplicand=domain_polynomial,
                        variables=polynomial_variables,
                    ).apply(state)

                    multipliers_entry[domain_name] = multiplier

                    sos_polynomial_entry = sos_polynomial_entry - multiplier * domain_polynomial

                    if domain_name in inequalities:
                        constraint_primitives.append(
                            init_sum_of_squares_primitive(
                                name=name,
                                expression=multiplier,
                                decision_variable_symbols=tuple(multiplier.iterate_symbols()),
                                polynomial_variables=polynomial_variables,
                            )
                        )

                multipliers[row, col] = multipliers_entry
                sos_certificates[row, col] = sos_polynomial_entry

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
            primitives=tuple(constraint_primitives),
            polynomial_variables=polynomial_variables,
            positive_matrix=positive_matrix,
            shape=(n_rows, n_cols),
            domain=domain,
            multipliers=multipliers,
            sos_certificates=sos_certificates,
        )

        return state, constraint
    
    return statemonad.get_map_put(create_constraint)
