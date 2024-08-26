from typing import override
from dataclasses import replace
from dataclassabc import dataclassabc

import polymat
from polymat.typing import (
    ExpressionTreeMixin,
    VariableExpression,
    MonomialVectorExpression,
    VariableVectorExpression,
)

from sosopt.polymat.from_ import define_variable
from sosopt.polymat.polynomialvariable import PolynomialVariable


@dataclassabc(frozen=True)
class PolynomialVariableImpl(PolynomialVariable):
    child: ExpressionTreeMixin
    coefficients: tuple[tuple[VariableExpression]]
    n_row: int
    n_col: int
    name: str
    monomials: MonomialVectorExpression
    polynomial_variables: VariableVectorExpression

    @override
    def copy(self, /, **changes):
        return replace(self, **changes)


def init_polynomial_variable(
    name: str,
    monomials: MonomialVectorExpression,
    polynomial_variables: VariableVectorExpression,
    n_row=1,
    n_col=1,
):
    def gen_rows():
        for row in range(n_row):

            def gen_cols():
                for col in range(n_col):
                    match (n_row, n_col):
                        case (1, 1):
                            elem_name = name
                        case (1, _):
                            elem_name = f"{name}_{col+1}"
                        case (_, 1):
                            elem_name = f"{name}_{row+1}"
                        case _:
                            elem_name = f"{name}_{row+1}_{col+1}"

                    # param = monom.parametrize(variable=OptVariable(elem_name))
                    param = define_variable(elem_name, size=monomials)

                    yield param, param.T @ monomials

            params, polys = tuple(zip(*gen_cols()))

            if 1 < len(polys):
                expr = polymat.h_stack(polys)
            else:
                expr = polys[0]

            yield params, expr

    params, polys = tuple(zip(*gen_rows()))

    if 1 < len(polys):
        expr = polymat.v_stack(polys)
    else:
        expr = polys[0]

    return PolynomialVariableImpl(
        name=name,
        monomials=monomials,
        coefficients=params,
        polynomial_variables=polynomial_variables,
        child=expr.child,
        n_row=n_row,
        n_col=n_col,
    )
