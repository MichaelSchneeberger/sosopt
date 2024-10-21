from typing import Iterable, NamedTuple

from donotation import do

from sosopt.utils.toquadraticsize import to_quadratic_size
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
    # cost
    lin_cost: ArrayRepr
    quad_cost: ArrayRepr | None

    # constraints
    nonneg_orthant: tuple[ArrayRepr, ...]
    second_order_cone: tuple[ArrayRepr, ...]
    semidef_cone: tuple[ArrayRepr, ...]
    equality: tuple[ArrayRepr, ...]

    # for debugging
    indices: tuple[int, ...]
    variable_names: tuple[str, ...]

    @property
    def n_var(self):
        return len(self.indices)

    def to_summary(self):
        def gen_summary():
            yield f'Number of variables: {self.n_var}'
            yield f'Quadratic cost: {self.quad_cost is not None}'

            if self.semidef_cone:
                yield 'Semidefinite constraints:'
                for array in self.semidef_cone:
                    size = to_quadratic_size(array.n_eq)
                    yield f'- {size}x{size}'

            if self.equality:
                yield 'Equality constraints:'
                for array in self.equality:
                    yield f'- {array.n_eq}'

            yield f'Variables: {self.variable_names}'

        return '\n'.join(gen_summary())


def to_solver_args(
    indices: VariableVectorExpression | tuple[int, ...],
    lin_cost: PolynomialExpression,
    quad_cost: VectorExpression | None = None,
    l_data: Iterable[tuple[str, VectorExpression]] | None = None,
    q_data: Iterable[tuple[str, VectorExpression]] | None = None,
    s_data: Iterable[tuple[str, VectorExpression]] | None = None,
    eq_data: Iterable[tuple[str, VectorExpression]] | None = None,
):
    def create_solver_args(state: State):
        match indices:
            case VariableVectorExpression():
                state, indices_ = polymat.to_variable_indices(indices).apply(state)
            case _:
                indices_ = indices

        def to_array(state: State, name: str, expr: MatrixExpression):
            state, array = polymat.to_array(
                name=name, expr=expr, variables=indices_
            ).apply(state)

            if 1 < array.degree:
                monomial_expr = expr.truncate_monomials(
                    variables=indices_, degrees=(array.degree,)
                ).to_linear_monomials(indices_)[0, 0]
                state, monomial = polymat.to_sympy(monomial_expr).apply(state)

                raise AssertionError(
                    (
                        f'The degree={array.degree} of the polynomial "{name}" in decision variables'
                        f" used to encode the optimization problem constraint must not exceed 1. "
                        f'However, the monomial "{monomial}" is of higher degree.'
                    )
                )

            return state, array

        state, lin_cost_array = to_array(state=state, name="linear_cost", expr=lin_cost)

        # maximum degree of cost function must be 2
        assert lin_cost_array.degree <= 1, f"{lin_cost_array.degree=}"

        if quad_cost is None:
            quad_cost_array = None

        else:
            state, quad_cost_array = to_array(
                state=state, name="quadratic_cost", expr=quad_cost
            )

            # maximum degree of cost function must be 2
            assert quad_cost_array.degree <= 1, f"{quad_cost_array.degree=}"

        l_data_arrays = []
        if l_data is not None:
            for name, expr in l_data:
                state, array = to_array(state=state, name=name, expr=expr)
                l_data_arrays.append(array)

        q_data_arrays = []
        if q_data is not None:
            for name, expr in q_data:
                state, array = to_array(state=state, name=name, expr=expr)
                q_data_arrays.append(array)

        s_data_arrays = []
        if s_data is not None:
            for name, expr in s_data:
                state, array = to_array(state=state, name=name, expr=expr)
                s_data_arrays.append(array)

        eq_data_arrays = []
        if eq_data is not None:
            for name, expr in eq_data:
                state, array = to_array(state=state, name=name, expr=expr)
                eq_data_arrays.append(array)

        variable_names = tuple(state.get_name(index) for index in indices_)

        return state, SolverArgs(
            lin_cost=lin_cost_array,
            quad_cost=quad_cost_array,
            nonneg_orthant=tuple(l_data_arrays),
            second_order_cone=tuple(q_data_arrays),
            semidef_cone=tuple(s_data_arrays),
            equality=tuple(eq_data_arrays),
            indices=indices_,
            variable_names=variable_names,
        )

    return statemonad.get_map_put(create_solver_args)
