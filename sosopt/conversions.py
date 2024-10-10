import numpy as np

from donotation import do

import statemonad

import polymat
from polymat.typing import PolynomialExpression, VectorExpression

from sosopt.polymat.from_ import define_variable
from sosopt.polynomialconstraints.from_ import sos_matrix_constraint


@do()
def to_linear_cost(name: str, lin_cost: PolynomialExpression, quad_cost: VectorExpression):
    # https://math.stackexchange.com/questions/2256241/writing-a-convex-quadratic-program-qp-as-a-semidefinite-program-sdp
    
    n_rows, _ = yield from polymat.to_shape(quad_cost)

    t = define_variable(name=f't_{name}')

    constraint = yield from sos_matrix_constraint(
        name=name,
        greater_than_zero=polymat.concat((
            (polymat.from_(np.eye(n_rows)), quad_cost),
            (quad_cost.T, t - lin_cost)
        ))
    )

    return statemonad.from_((t, constraint))
