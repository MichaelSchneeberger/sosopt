from __future__ import annotations

from polymat.typing import (
    VariableVectorExpression,
    PolynomialExpression,
)


def to_gram_matrix(polynomial: PolynomialExpression, variable: VariableVectorExpression):
    return polynomial.quadratic_in(
        variables=variable,
    )
