import numpy as np

import statemonad

import polymat
from polymat.typing import ScalarPolynomialExpression, VectorExpression, MatrixExpression

from sosopt.polymat.from_ import define_variable
from sosopt.polynomialconstraints.from_ import sos_matrix_constraint


def to_linear_cost(
    name: str, 
    quad_cost: VectorExpression,
    lin_cost: ScalarPolynomialExpression | None = None, 
):
    # https://math.stackexchange.com/questions/2256241/writing-a-convex-quadratic-program-qp-as-a-semidefinite-program-sdp
    
    def _to_linear_cost(state):

        state, (n_rows, _) = polymat.to_shape(quad_cost).apply(state)

        t = define_variable(name=f't_{name}')

        match lin_cost:
            case None:
                d = t
            case MatrixExpression():
                d = t - lin_cost

        state, constraint = sos_matrix_constraint(
            name=name,
            greater_than_zero=polymat.concat((
                (polymat.from_(np.eye(n_rows)), quad_cost),
                (quad_cost.T, d)
            ))
        ).apply(state)

        return state, (t, constraint)

    return statemonad.get_map_put(_to_linear_cost)
