from __future__ import annotations

from donotation import do

import polymat
from polymat.typing import (
    MatrixExpression,
    PolynomialExpression,
    SymmetricMatrixExpression,
)

from sosopt.constraints.init import (
    init_zero_polynomial_constraint,
    to_positive_polynomial_constraint,
    to_putinar_psatz_constraint,
)
from sosopt.semialgebraicset import SemialgebraicSet


def zero_polynomial_constraint(
    name: str,
    equal_to_zero: MatrixExpression,
):
    return init_zero_polynomial_constraint(
        name=name,
        condition=equal_to_zero,
    )


def sos_constraint(
    name: str,
    greater_than_zero: PolynomialExpression | None = None,
    less_than_zero: PolynomialExpression | None = None,
):    
    if greater_than_zero is not None:
        condition = greater_than_zero
    elif less_than_zero is not None:
        condition = -less_than_zero
    else:
        raise Exception("SOS constraint requires condition.")

    return to_positive_polynomial_constraint(
        name=name,
        condition=condition,
    )


@do()
def sos_constraint_matrix(
    name: str,
    greater_than_zero: SymmetricMatrixExpression | None = None,
    less_than_zero: SymmetricMatrixExpression | None = None,
):
    if greater_than_zero is not None:
        condition = greater_than_zero
    elif less_than_zero is not None:
        condition = -less_than_zero
    else:
        raise Exception("SOS constraint requires condition.")

    shape = yield from polymat.to_shape(condition)

    x = polymat.define_variable(f"{name}_x", size=shape[0])

    return sos_constraint(
        name=name,
        greater_than_zero=x.T @ condition @ x,
    )


def sos_constraint_putinar(
    name: str,
    domain: SemialgebraicSet,
    greater_than_zero: PolynomialExpression | None = None,
    less_than_zero: PolynomialExpression | None = None,
):
    if greater_than_zero is not None:
        condition = greater_than_zero
    elif less_than_zero is not None:
        condition = -less_than_zero
    else:
        raise Exception("SOS constraint requires condition.")

    return to_putinar_psatz_constraint(
        name,
        condition=condition,
        domain=domain,
    )