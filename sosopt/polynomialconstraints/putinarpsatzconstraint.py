from __future__ import annotations

from dataclasses import replace

from dataclassabc import dataclassabc

from sosopt.state.state import State
import statemonad

import polymat
from polymat.typing import (
    MatrixExpression,
    ScalarPolynomialExpression,
)

from sosopt.polynomialconstraints.constraintprimitives.polynomialconstraintprimitive import (
    PolynomialConstraintPrimitive,
)
from sosopt.polynomialconstraints.constraintprimitives.decisionvariablesmixin import to_decision_variable_symbols
from sosopt.polynomialconstraints.polynomialvariablesmixin import (
    PolynomialVariablesMixin,
    to_polynomial_variable_indices,
)
from sosopt.polymat.from_ import define_multiplier
from sosopt.polymat.sources.polynomialvariable import ScalarPolynomialVariable
from sosopt.semialgebraicset import SemialgebraicSet
from sosopt.polynomialconstraints.polynomialconstraint import PolynomialConstraint
from sosopt.polynomialconstraints.constraintprimitives.sumofsquaresprimitive import (
    init_sum_of_squares_primitive,
)


@dataclassabc(frozen=True, slots=True)
class PutinarPsatzConstraint(PolynomialVariablesMixin, PolynomialConstraint):
    name: str  # override
    primitives: tuple[PolynomialConstraintPrimitive, ...]  # override
    polynomial_variable_indices: tuple[int, ...]  # override

    # the parametrized polynomial matrix that is rquired to be positive in each entry on the domain
    positive_matrix: MatrixExpression

    # shape of the polynomial matrix
    shape: tuple[int, int]

    # domain defined by the intersection of zero-sublevel sets of a set of polynomials
    domain: SemialgebraicSet | None

    # multipliers used to build the SOS certificate for each entry in the matrix
    multipliers: dict[str, ScalarPolynomialVariable]

    # SOS certificate required to prove the non-negativity of the target polynomials
    # (for each entry in the matrix) over the domain
    sos_certificate: ScalarPolynomialExpression

    def copy(self, /, **others):
        return replace(self, **others)


@dataclassabc(frozen=True, slots=True)
class PutinarPsatzMatrixConstraint(PolynomialVariablesMixin, PolynomialConstraint):
    name: str  # override
    primitives: tuple[PolynomialConstraintPrimitive, ...]  # override
    polynomial_variable_indices: tuple[int, ...]  # override

    # the parametrized polynomial matrix that is rquired to be positive in each entry on the domain
    positive_matrix: MatrixExpression

    # shape of the polynomial matrix
    shape: tuple[int, int]

    # domain defined by the intersection of zero-sublevel sets of a set of polynomials
    domain: SemialgebraicSet | None

    # multipliers used to build the SOS certificate for each entry in the matrix
    multipliers: dict[tuple[int, int], dict[str, ScalarPolynomialVariable]]

    # SOS certificate required to prove the non-negativity of the target polynomials
    # (for each entry in the matrix) over the domain
    sos_certificates: dict[tuple[int, int], ScalarPolynomialExpression]

    def copy(self, /, **others):
        return replace(self, **others)


def init_putinar_psatz_constraint(
    name: str,
    expression: MatrixExpression,
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

        vector = polymat.v_stack(
            (expression.reshape(-1, 1),) + tuple(domain_polynomials.values())
        ).to_vector()

        state, polynomial_indices = to_polynomial_variable_indices(vector).apply(state)

        state, max_domain_degrees = polymat.to_degree(
            expr=vector, variables=polynomial_indices
        ).apply(state)
        max_domain_degree = max(max(max_domain_degrees))

        state, shape = polymat.to_shape(expression).apply(state)
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
                condition_entry = expression[row, col]

                state, max_cond_degrees = polymat.to_degree(
                    condition_entry,
                    variables=polynomial_indices,
                ).apply(state)
                max_cond_degree = max(max(max_cond_degrees))

                sos_certificate = condition_entry
                multipliers_entry = {}

                for domain_name, domain_polynomial in domain_polynomials.items():
                    multiplier_name = get_name(row, col, domain_name)

                    state, multiplier = define_multiplier(
                        name=multiplier_name,
                        degree=max(max_domain_degree, max_cond_degree),
                        multiplicand=domain_polynomial,
                        variables=polynomial_indices,
                    ).apply(state)

                    multipliers_entry[domain_name] = multiplier

                    sos_certificate = (
                        sos_certificate - multiplier * domain_polynomial
                    )

                    if domain_name in inequalities:
                        constraint_primitives.append(
                            init_sum_of_squares_primitive(
                                name=multiplier_name,
                                expression=multiplier,
                                decision_variable_symbols=tuple(multiplier.iterate_symbols()),
                                polynomial_variable_indices=polynomial_indices,
                                sparse_smr=state.sparse_smr,
                            )
                        )

                multipliers[row, col] = multipliers_entry
                sos_certificates[row, col] = sos_certificate

                state, decision_variable_symbols = to_decision_variable_symbols(sos_certificate).apply(state)

                constraint_primitives.append(
                    init_sum_of_squares_primitive(
                        name=name,
                        expression=sos_certificate,
                        polynomial_variable_indices=polynomial_indices,
                        decision_variable_symbols=decision_variable_symbols,
                        sparse_smr=state.sparse_smr,
                    )
                )

        match shape:
            case (1, 1):
                constraint = PutinarPsatzConstraint(
                    name=name,
                    primitives=tuple(constraint_primitives),
                    polynomial_variable_indices=polynomial_indices,
                    positive_matrix=expression,
                    shape=shape,
                    domain=domain,
                    multipliers=multipliers[0, 0],
                    sos_certificate=sos_certificates[0, 0],
                )

            case _:
                constraint = PutinarPsatzMatrixConstraint(
                    name=name,
                    primitives=tuple(constraint_primitives),
                    polynomial_variable_indices=polynomial_indices,
                    positive_matrix=expression,
                    shape=shape,
                    domain=domain,
                    multipliers=multipliers,
                    sos_certificates=sos_certificates,
                )

        return state, constraint

    return statemonad.get_map_put(create_constraint)
