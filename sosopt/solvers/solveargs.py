from typing import Iterable, NamedTuple

from donotation import do

import statemonad

import polymat
from polymat.typing import ArrayRepr, PolynomialExpression, VectorExpression, VariableVectorExpression


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
        l_data: Iterable[VectorExpression] | None = None,
        q_data: Iterable[VectorExpression] | None = None,
        s_data: Iterable[VectorExpression] | None = None,
):
    lin_cost_array = yield from polymat.to_array(lin_cost, indices)

    # maximum degree of cost function must be 2
    assert lin_cost_array.degree <= 1, f"{lin_cost_array.degree=}"

    if quad_cost is None:
        quad_cost_array = None
    else:
        quad_cost_array = yield from polymat.to_array(quad_cost, indices)

        # maximum degree of cost function must be 2
        assert quad_cost_array.degree <= 1, f"{quad_cost_array.degree=}"

    if l_data is None:
        l_data_array = tuple()
    else:
        l_data_array = yield from statemonad.zip(
            (polymat.to_array(e, indices) for e in l_data)
        )

    if q_data is None:
        q_data_array = tuple()
    else:
        q_data_array = yield from statemonad.zip(
            (polymat.to_array(e, indices) for e in q_data)
        )

    if s_data is None:
        s_data_array = tuple()
    else:
        s_data_array = yield from statemonad.zip(
            (polymat.to_array(e, indices) for e in s_data)
        )

    # maximum degree of constraint must not be greater than 1
    # the assertion is defined inside a function because the do-notation forbits for loops
    def assert_degree_of_constraints():
        for array in l_data_array + q_data_array + s_data_array:
            if 1 < array.degree:
                raise AssertionError(
                    (
                        "The degree of the polynomial in the decision variables used to encode the optimization problem constraints "
                        "must not exceed 1."
                    )
                )

    assert_degree_of_constraints()

    return statemonad.from_(
        SolverArgs(
            lin_cost=lin_cost_array,
            quad_cost=quad_cost_array,
            l_data=l_data_array,
            q_data=q_data_array,
            s_data=s_data_array,
        )
    )
