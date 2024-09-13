from typing import Iterable, NamedTuple

from donotation import do

import statemonad

import polymat
from polymat.typing import (
    State,
    ArrayRepr,
    MatrixExpression,
    PolynomialExpression,
    VectorExpression,
    VariableVectorExpression,
)


class SolverArgs(NamedTuple):
    lin_cost: ArrayRepr
    quad_cost: ArrayRepr | None
    l_data: tuple[ArrayRepr, ...]
    q_data: tuple[ArrayRepr, ...]
    s_data: tuple[ArrayRepr, ...]


@do()
def get_solver_args(
    indices: VariableVectorExpression | tuple[int, ...],
    lin_cost: PolynomialExpression,
    quad_cost: VectorExpression | None = None,
    l_data: Iterable[tuple[str, VectorExpression]] | None = None,
    q_data: Iterable[tuple[str, VectorExpression]] | None = None,
    s_data: Iterable[tuple[str, VectorExpression]] | None = None,
):
    @do()
    def to_array(name, expr: MatrixExpression):
        array = yield from polymat.to_array(name=name, expr=expr, variables=indices)

        if 1 < array.degree:

            monomial_expr = expr.truncate_monomials(variables=indices, degrees=(array.degree,)).to_linear_monomials(indices)[0, 0]
            monomial = yield from polymat.to_sympy(monomial_expr)

            raise AssertionError(
                (
                    f'The degree={array.degree} of the polynomial "{name}" in decision variables'
                    f' used to encode the optimization problem constraint must not exceed 1. '
                    f'However, the monomial "{monomial}" is of higher degree.'
                )
            )

        return statemonad.from_[State](array)

    lin_cost_array = yield from to_array(name="linear_cost", expr=lin_cost)

    # maximum degree of cost function must be 2
    assert lin_cost_array.degree <= 1, f"{lin_cost_array.degree=}"

    if quad_cost is None:
        quad_cost_array = None
    else:
        quad_cost_array = yield from to_array(name="quadratic_cost", expr=quad_cost)

        # maximum degree of cost function must be 2
        assert quad_cost_array.degree <= 1, f"{quad_cost_array.degree=}"

    if l_data is None:
        l_data_array = tuple()
    else:
        l_data_array = yield from statemonad.zip(
            (to_array(name=name, expr=expr) for name, expr in l_data)
        )

    if q_data is None:
        q_data_array = tuple()
    else:
        q_data_array = yield from statemonad.zip(
            (to_array(name=name, expr=expr) for name, expr in q_data)
        )

    if s_data is None:
        s_data_array = tuple()
    else:
        s_data_array = yield from statemonad.zip(
            (to_array(name=name, expr=expr) for name, expr in s_data)
        )

    # # maximum degree of constraint must not be greater than 1
    # # the assertion is defined inside a function because the do-notation forbits for loops
    # def assert_degree_of_constraints():
    #     for array in l_data_array + q_data_array + s_data_array:
    #         if 1 < array.degree:
    #             raise AssertionError(
    #                 (
    #                     "The degree of the polynomial in the decision variables used to encode the optimization problem constraints "
    #                     "must not exceed 1."
    #                 )
    #             )

    # assert_degree_of_constraints()

    return statemonad.from_(
        SolverArgs(
            lin_cost=lin_cost_array,
            quad_cost=quad_cost_array,
            l_data=l_data_array,
            q_data=q_data_array,
            s_data=s_data_array,
        )
    )
