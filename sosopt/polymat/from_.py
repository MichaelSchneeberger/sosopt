from __future__ import annotations
from typing import Iterator

import statemonad

import polymat
from polymat.typing import (
    MatrixExpression,
    VariableVectorExpression,
    MonomialVectorExpression,
)

from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol
from sosopt.polymat.init import init_polynomial_variable


def define_variable(
    name: DecisionVariableSymbol | str,
    size: int | MatrixExpression | None = None,
):
    """
    Defines a decision variable of the SOS optimizaton problem.
    """
    
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


def define_polynomial(
    name: str,
    monomials: MonomialVectorExpression | None = None,
    polynomial_variables: VariableVectorExpression | None = None,
    n_rows: int = 1,
    n_cols: int = 1,
):
    """
    Defines a polynomial matrix variable as a `polymat.typing.MatrixExpression`, 
    where the coefficients of the polynomials are decision variables. The polynomial 
    matrix is represented by a combination of monomials, decision variable coefficients, 
    and polynomial variables.

    Parameters:
    ----------
    name : str
        The name assigned to the polynomial matrix variable.
    monomials : MonomialVectorExpression, optional
        A vector of monomials that determines the structure of the polynomial matrix. If None, 
        monomials are assumed to be a single element 1.
    polynomial_variables : VariableVectorExpression, optional
        A vector of polynomial variables used to define the polynomial matrix. If None, 
        no polynomial variables are considered, reducing the polynomial variable to a constant variable.
    n_rows : int, optional
        The number of rows of the resulting polynomial matrix.
    n_cols : int, optional
        The number of columns of the resulting polynomial matrix.
        
    Returns:
    --------
    PolynomialMatrix:
        A matrix of polynomial expressions where the coefficients are decision variables.
        This matrix is equipped with its monomial terms, coefficients, and polynomial variables.

    Example:
    --------
    ```python
    x = polymat.define_variable('x')

    # Define a polynomial matrix variable 'p' with specific monomials and polynomial variables
    p = sosopt.define_polynomial(
        name='p',
        monomials=x.combinations((0, 1, 2)),  # Monomial vector for degrees 0, 1, and 2
        polynomial_variables=x,               # Polynomial variables used in 'p'
    )

    # Convert polynomial matrix 'p' to sympy representation and print
    state, p_sympy = polymat.to_sympy(p).apply(state)
    # Expected output: p_sympy = p_0 + p_1*x + p_2*x**2
    print(f'{p_sympy=}')

    # Convert and print the monomial vector
    state, monom_sympy = polymat.to_sympy(p.monomials.T).apply(state)
    # Expected output: monom_sympy = Matrix([[1, x, x**2]])
    print(f'{monom_sympy=}')

    # Convert and print the coefficient vector
    state, coeff_sympy = polymat.to_sympy(p.to_coefficient_vector().T).apply(state)
    # Expected output: coeff_sympy = Matrix([[p_0, p_1, p_2]])
    print(f'{coeff_sympy=}')
    ```
    """

    match (monomials, polynomial_variables):
        case (None, None):
            # empty variable vector
            polynomial_variables = polymat.from_variable_indices(tuple())
            monomials = polymat.from_(1).to_monomial_vector()
        case (None, _) | (_, None):
            raise Exception(
                "Both `monomials` and `polynomial_variables` must either be provided or set to None otherwise."
            )
        
    shape = n_rows, n_cols

    match shape:
        case (1, 1):
            get_name = lambda r, c: name  # noqa: E731
        case (1, _):
            get_name = lambda r, c: f"{name}_{c+1}"  # noqa: E731
        case (_, 1):
            get_name = lambda r, c: f"{name}_{r+1}"  # noqa: E731
        case _:
            get_name = lambda r, c: f"{name}_{r+1}_{c+1}"  # noqa: E731

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

    coefficients, row_vectors = tuple(zip(*gen_rows()))

    if 1 < len(row_vectors):
        expr = polymat.v_stack(row_vectors)
    else:
        expr = row_vectors[0]

    return init_polynomial_variable(
        name=name,
        monomials=monomials,
        coefficients=coefficients,
        polynomial_variables=polynomial_variables,
        child=expr.child,
        shape=shape,
    )


def define_multiplier(
    name: str,
    degree: int,
    multiplicand: MatrixExpression,
    variables: VariableVectorExpression,
):
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

    def create_multiplier(state):
        state, multiplicand_degrees = polymat.to_degree(
            multiplicand, variables=variables
        ).apply(state)
        max_degree_multiplicand = max(max(multiplicand_degrees))
        degrees = max_degree - max_degree_multiplicand
        degree_range = tuple(range(int(degrees) + 1))
        expr = define_polynomial(
            name=name,
            monomials=variables.combinations(degree_range).cache(),
            polynomial_variables=variables,
        )
        return state, expr

    return statemonad.get_map_put(create_multiplier)


def define_symmetric_matrix(
    name: str,
    size: int,
    monomials: MonomialVectorExpression | None = None,
    polynomial_variables: VariableVectorExpression | None = None,
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

    entries = {}

    def gen_rows():
        for row in range(size):

            def gen_cols():
                for col in range(size):
                    if row <= col:
                        param = define_variable(
                            name=f"{name}_{row+1}_{col+1}",
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


def v_stack(expressions: Iterator[MatrixExpression]) -> MatrixExpression:
    return polymat.v_stack(expressions)
