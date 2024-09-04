from typing import override
from dataclasses import replace
from dataclassabc import dataclassabc

import polymat
from polymat.typing import (
    ExpressionNode,
    VariableExpression,
    MonomialVectorExpression,
    VariableVectorExpression,
    MatrixExpression,
)

from sosopt.polymat.decisionvariableexpression import DecisionVariableExpression
from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol
from sosopt.polymat.polynomialvariable import PolynomialVariable


@dataclassabc(frozen=True)
class DecisionVariableExpressionImpl(DecisionVariableExpression):
    child: ExpressionNode
    symbol: DecisionVariableSymbol

    @override
    def copy(self, /, **changes):
        return replace(self, **changes)


def init_decision_variable_expression(child: ExpressionNode, symbol: DecisionVariableSymbol):
    return DecisionVariableExpressionImpl(
        child=child,
        symbol=symbol,
    )


@dataclassabc(frozen=True)
class PolynomialVariableImpl(PolynomialVariable):
    name: str
    child: ExpressionNode
    coefficients: tuple[tuple[VariableExpression]]
    shape: tuple[int, int]
    monomials: MonomialVectorExpression
    polynomial_variables: VariableVectorExpression

    @override
    def copy(self, /, **changes):
        return replace(self, **changes)


def init_polynomial_variable(
    name: str,
    child: ExpressionNode,
    coefficients: tuple[tuple[VariableExpression]],
    monomials: MonomialVectorExpression,
    polynomial_variables: VariableVectorExpression,
    shape: tuple[int, int] = (1, 1),
):
    return PolynomialVariableImpl(
        name=name,
        monomials=monomials,
        coefficients=coefficients,
        polynomial_variables=polynomial_variables,
        child=child,
        shape=shape,
    )


# def init_symmetric_matrix_variable(
#     name: str,
#     monomials: MonomialVectorExpression,
#     polynomial_variables: VariableVectorExpression,
#     size: int,
# ):
#     entries = {}

#     def gen_rows():
#         for row in range(size):

#             def gen_cols():
#                 for col in range(size):
#                     if row <= col:
#                         param = define_variable(
#                             name=f"{name}{row+1}{col+1}",
#                             size=monomials,
#                         )
#                         entry = param, param.T @ monomials

#                         entries[row, col] = entry

#                         yield entry
#                     else:
#                         yield entries[col, row]

#             params, polynomials = tuple(zip(*gen_cols()))
#             yield params, polymat.h_stack(polynomials)

#     params, row_vectors = tuple(zip(*gen_rows()))

#     expr = polymat.v_stack(row_vectors)

#     return PolynomialVariableImpl(
#         name=name,
#         monomials=monomials,
#         coefficients=params,
#         polynomial_variables=polynomial_variables,
#         child=expr.child,
#         shape=(size, size),
#     )


# def init_polynomial_variable(
#     name: str,
#     monomials: MonomialVectorExpression | None = None,
#     polynomial_variables: VariableVectorExpression | None = None,
#     shape: tuple[int, int] = (1, 1),
# ):
#     match (monomials, polynomial_variables):
#         case (None, None):
#             # empty variable vector
#             polynomial_variables = polymat.from_variable_indices(tuple())
#             monomials = polymat.from_(1).to_monomial_vector()
#         case (None, _) | (_, None):
#             raise Exception(
#                 "Both `monomials` and `polynomial_variables` must either be provided or set to None otherwise."
#             )

#     match shape:
#         case (1, 1):
#             get_name = lambda r, c: name  # noqa: E731
#         case (1, _):
#             get_name = lambda r, c: f"{name}{c+1}"  # noqa: E731
#         case (_, 1):
#             get_name = lambda r, c: f"{name}{r+1}"  # noqa: E731
#         case _:
#             get_name = lambda r, c: f"{name}{r+1}{c+1}"  # noqa: E731

#     n_rows, n_cols = shape

#     def gen_rows():
#         for row in range(n_rows):

#             def gen_cols():
#                 for col in range(n_cols):
#                     param = define_variable(
#                         name=get_name(row, col),
#                         size=monomials,
#                     )

#                     yield param, param.T @ monomials

#             params, polynomials = tuple(zip(*gen_cols()))

#             if 1 < len(polynomials):
#                 expr = polymat.h_stack(polynomials)
#             else:
#                 expr = polynomials[0]

#             yield params, expr

#     params, row_vectors = tuple(zip(*gen_rows()))

#     if 1 < len(row_vectors):
#         expr = polymat.v_stack(row_vectors)
#     else:
#         expr = row_vectors[0]

#     return PolynomialVariableImpl(
#         name=name,
#         monomials=monomials,
#         coefficients=params,
#         polynomial_variables=polynomial_variables,
#         child=expr.child,
#         shape=shape,
#     )
