from __future__ import annotations
from typing import Iterator

from donotation import do
import statemonad
from statemonad.typing import StateMonad

import polymat
from polymat.typing import (
    State,
    MatrixExpression,
    VariableVectorExpression,
    MonomialVectorExpression,
)

from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol
from sosopt.polymat.init import init_polynomial_variable
from sosopt.polymat.polynomialvariable import PolynomialVariable


def define_multiplier(
    name: str,
    degree: int,
    multiplicand: MatrixExpression,
    variables: VariableVectorExpression,
) -> StateMonad[State, PolynomialVariable]:
    """
    Defines a polynomial multiplier intended to be multiplied with a given polynomial 
    (the multiplicand), ensuring that the resulting product does not exceed a specified degree.

    Parameters:
    ----------
    name : str
        The name assigned to the multiplier polynomial variable.
    degree : int
        The maximum allowed degree for the product of the multiplicand and multiplier.
    multiplicand : MatrixExpression
        The polynomial to be multiplied with the multiplier.
    variables : VariableVectorExpression
        The polynomial variables used to determine the degree of the resulting polynomial.

    Example:
    --------
    ```python
    P = polymat.from_([
        [x**2 - 2*x + 2, x],
        [x, x**2],
    ])

    state, m = sosopt.define_multiplier(
        name='m',           # name of the polynomial variable
        degree=4,           # maximum degree of the product P*m
        multiplicand=P,
        variables=x,        # polynomial variables determining the degree
    ).apply(state)

    state, m_sympy = polymat.to_sympy(m).apply(state)

    # Expected output: m_sympy = m_0 + m_1*x + m_2*x**2
    print(f'{m_sympy=}')
    ```
    
    Returns:
    --------
    Multiplier:
        A polynomial expression parameterized as a decision variable, representing the multiplier 
        constrained by the specified degree.
    """

    def round_up_to_even(n):
        if n % 2 == 0:
            return n
        else:
            return n + 1

    max_degree = round_up_to_even(degree)

    @do()
    def create_multiplier():
        multiplicand_degrees = yield from polymat.to_degree(
            multiplicand, variables=variables
        )
        max_degree_multiplicand = int(max(multiplicand_degrees.reshape(-1)))
        degrees = max_degree - max_degree_multiplicand
        degree_range = tuple(range(int(degrees) + 1))
        expr = define_polynomial(
            name=name,
            monomials=variables.combinations(degree_range).cache(),
            polynomial_variables=variables,
        )
        return statemonad.from_[State](expr)

    return create_multiplier()


def define_symmetric_matrix(
    name: str,
    monomials: MonomialVectorExpression,
    polynomial_variables: VariableVectorExpression,
    size: int,
):
    entries = {}

    def gen_rows():
        for row in range(size):

            def gen_cols():
                for col in range(size):
                    if row <= col:
                        param = define_variable(
                            name=f"{name}{row+1}{col+1}",
                            size=monomials,
                        )
                        entry = param, param.T @ monomials

                        entries[row, col] = entry

                        yield entry
                    else:
                        yield entries[col, row]

            params, polynomials = tuple(zip(*gen_cols()))
            yield params, polymat.h_stack(polynomials)

    params, row_vectors = tuple(zip(*gen_rows()))

    expr = polymat.v_stack(row_vectors)

    return init_polynomial_variable(
        name=name,
        monomials=monomials,
        coefficients=params,
        polynomial_variables=polynomial_variables,
        child=expr.child,
        shape=(size, size),
    )


def define_polynomial(
    name: str,
    monomials: MonomialVectorExpression | None = None,
    polynomial_variables: VariableVectorExpression | None = None,
    shape: tuple[int, int] = (1, 1),
):
    match (monomials, polynomial_variables):
        case (None, None):
            # empty variable vector
            polynomial_variables = polymat.from_variable_indices(tuple())
            monomials = polymat.from_(1).to_monomial_vector()
        case (None, _) | (_, None):
            raise Exception(
                "Both `monomials` and `polynomial_variables` must either be provided or set to None otherwise."
            )

    match shape:
        case (1, 1):
            get_name = lambda r, c: name  # noqa: E731
        case (1, _):
            get_name = lambda r, c: f"{name}{c+1}"  # noqa: E731
        case (_, 1):
            get_name = lambda r, c: f"{name}{r+1}"  # noqa: E731
        case _:
            get_name = lambda r, c: f"{name}{r+1}{c+1}"  # noqa: E731

    n_rows, n_cols = shape

    def gen_rows():
        for row in range(n_rows):

            def gen_cols():
                for col in range(n_cols):
                    param = define_variable(
                        name=get_name(row, col),
                        size=monomials,
                    )

                    yield param, param.T @ monomials

            params, polynomials = tuple(zip(*gen_cols()))

            if 1 < len(polynomials):
                expr = polymat.h_stack(polynomials)
            else:
                expr = polynomials[0]

            yield params, expr

    params, row_vectors = tuple(zip(*gen_rows()))

    if 1 < len(row_vectors):
        expr = polymat.v_stack(row_vectors)
    else:
        expr = row_vectors[0]

    return init_polynomial_variable(
        name=name,
        monomials=monomials,
        coefficients=params,
        polynomial_variables=polynomial_variables,
        child=expr.child,
        shape=shape,
    )


def define_variable(
    name: DecisionVariableSymbol | str,
    size: int | MatrixExpression | None = None,
):
    
    if not isinstance(name, DecisionVariableSymbol):
        symbol = DecisionVariableSymbol(name)
    else:
        symbol = name

    return polymat.define_variable(name=symbol, size=size)

    # if isinstance(size, MatrixExpression):
    #     n_size = size.child
    # else:
    #     n_size = size

    # child=init_define_variable(
    #     symbol=symbol, size=n_size, stack=get_frame_summary()
    # )

    # return init_decision_variable_expression(
    #     child=child,
    #     symbol=symbol,
    # )


def v_stack(expressions: Iterator[MatrixExpression]) -> MatrixExpression:
    return polymat.v_stack(expressions)
