from __future__ import annotations

import statemonad

import polymat
from polymat.typing import (
    MatrixExpression,
    VariableVectorExpression,
    MonomialVectorExpression,
)

from sosopt.polymat.symbols.auxiliaryvariablesymbol import AuxiliaryVariableSymbol
from sosopt.polymat.symbols.decisionvariablesymbol import DecisionVariableSymbol
from sosopt.polymat.init import (
    init_polynomial_variable,
    init_sos_monomial_basis,
    init_sos_monomial_basis_sparse,
    init_gram_matrix,
    init_gram_matrix_sparse,
)


def gram_matrix(
    expression: MatrixExpression,
    variables: MatrixExpression,
    monomials: MatrixExpression | None = None,
    auxilliary_variable_symbol: AuxiliaryVariableSymbol | None = None,
    sparse_smr: bool | None = None,
):
    """
    Performs an SOS decomposition to retrieve the SMR from a polynomial expression.

    Args:
        expression: Defines the expression $p(x)$ that can be written
            as $p(x) = Z(x)^T Q Z(x)$ for some a monomial vector $Z(x)$.
        variables: Defines the polynomial variables.
        monomials: Defines the monomial vector $Z(x)$.
        sparse_smr: If True, no SOS decomposition variables are defined.
    """

    if sparse_smr is None:
        sparse_smr = True

    if sparse_smr:
        node = init_gram_matrix_sparse(
            child=expression,
            variables=variables,
            monomials=monomials,
        )
    else:
        node = init_gram_matrix(
            child=expression,
            variables=variables,
            monomials=monomials,
            auxilliary_variable_symbol=auxilliary_variable_symbol,
        )

    return polymat.from_(node).symmetric()


def sos_monomial_basis(
    expression: MatrixExpression,
    variables: MatrixExpression,
    sparse_smr: bool | None = None,
):
    """
    Defines an SOS monomial basis $Z(x)$ used for SOS decomposition.

    Args:
        expression: Defines the expression $p(x)$ that can be written
            as $p(x) = Z(x)^T Q Z(x)$ for some a monomial vector $Z(x)$.
        variables: Defines the polynomial variables.
        sparse_smr: If True, no SOS decomposition variables are defined
    """

    if sparse_smr is None:
        sparse_smr = True

        print(sparse_smr)

    if sparse_smr:
        node = init_sos_monomial_basis_sparse(
            child=expression,
            variables=variables,
        )
    else:
        node = init_sos_monomial_basis(
            child=expression,
            variables=variables,
        )

    return polymat.from_(node)



def define_variable(
    name: DecisionVariableSymbol | str,
    size: int | MatrixExpression | None = None,
):
    """
    Defines a decision variable for the SOS Problem.

    Args:
        name: The name assigned to the variable. This name needs to be unique.
        size: The size of the decision variables. This is either given by an integer or derived
            from the shape of a polynomial expression.

    Returns:
        (VariableVectorSymbolExpression): A polynomial variable expression

    Example:
        ``` python
        like = polymat.from_(np.ones((3, 2)))

        # creates a variable of size 6
        x = sosopt.define_variable('x', size=like)
        ```
    """

    if not isinstance(name, DecisionVariableSymbol):
        symbol = DecisionVariableSymbol(name)
    else:
        symbol = name

    return polymat.define_variable(name=symbol, size=size)


def define_polynomial(
    name: str,
    monomials: MonomialVectorExpression | None = None,
    n_rows: int | None = None,
    n_cols: int | None = None,
    like: MatrixExpression | None = None,
):
    """
    Defines of a fully parametrized polynomial -- involving the specification of a decision variable
    for each coefficient of the polynomial.

    Args:
        name: The name assigned to the parametrized polynomial. This defines the name of the
            decision variable for each coefficient of the polynomial.
        monomials: Optional monomial vector that determines the structure of the polynomial matrix. If None,
            monomials are assumed to be a single element 1.
        n_rows: The number of rows of the resulting polynomial matrix.
        n_cols: The number of columns of the resulting polynomial matrix.
        like: Copy the number of rows and columns from the given polynomial expression.

    Returns:
        (StateMonad[MatrixExpression]): A polynomial expression where the coefficients are decision variables.

    Example:
        ``` python
        x = polymat.define_variable('x')

        # Define a parametrized polynomial specified by a monomial vector
        state, r = sosopt.define_polynomial(
            name='r',
            monomials=x.combinations((0, 1, 2)),
        ).apply(state)

        # returns a polymat vector [r_0, r_1, r_2] containing the coefficients
        r.coefficient
        ```
    """

    if monomials is None:
        monomials = polymat.from_(1).to_monomial_vector()

    def _define_polynomial(state):
        match (n_rows, n_cols, like):
            case None, None, None:
                shape = 1, 1
            case None, None, MatrixExpression():
                state, shape = polymat.to_shape(like).apply(state)
            case None, int() as nc, None:
                shape = (1, nc)
            case int() as nr, None, None:
                shape = (nr, 1)
            case int() as nr, int() as nc, _:
                shape = (nr, nc)
            case _:
                ValueError("Invalid shape specification")

        match shape:
            case (1, 1):
                get_name = lambda r, c: name  # noqa: E731
            case (1, _):
                get_name = lambda r, c: f"{name}_{c + 1}"  # noqa: E731
            case (_, 1):
                get_name = lambda r, c: f"{name}_{r + 1}"  # noqa: E731
            case _:
                get_name = lambda r, c: f"{name}_{r + 1}_{c + 1}"  # noqa: E731

        def gen_rows():
            for row in range(shape[0]):

                def gen_cols():
                    for col in range(shape[1]):
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

        expr = init_polynomial_variable(
            name=name,
            monomials=monomials,
            coefficients=coefficients,
            child=expr.child,
            shape=shape,
        )

        return state, expr

    return statemonad.get_map_put(_define_polynomial)


def define_multiplier(
    name: str,
    degree: int | MatrixExpression,
    variables: VariableVectorExpression | tuple[int, ...],
    multiplicand: MatrixExpression | None = None,
):
    """
    Defines a polynomial multiplier intended to be multiplied with a given polynomial
    (the multiplicand), ensuring that the resulting product does not exceed a specified degree.

    Args:
        name: The name assigned to the multiplier polynomial variable. This defines the name of the
            decision variable for each coefficient of the multiplier.
        degree: The maximum allowed degree for the product of the multiplicand and multiplier.
        multiplicand: The polynomial to be multiplied with the multiplier.
        variables: The polynomial variables used to determine the degree of the resulting polynomial.

    Returns:
        (StateMonad[ScalarPolynomialExpression]): A polynomial expression parameterized as a decision variable,
            representing the multiplier constrained by the specified degree.

    Example:
        ```python
        Q = polymat.from_([
            [x**2 - 2*x + 2, x],
            [x, x**2],
        ])

        state, m = sosopt.define_multiplier(
            name='m',           # name of the polynomial variable
            degree=4,           # maximum degree of the product P*m
            multiplicand=Q,
            variables=x,        # polynomial variables determining the degree
        ).apply(state)
        ```
    """

    def _define_multiplier(state, degree=degree):
        if isinstance(degree, MatrixExpression):
            # Compute the degree of the denominator s(x)
            state, max_degree_multiplier = polymat.to_degree(degree, variables=variables).apply(state)
            degree = max(max(max_degree_multiplier))

        else:
            assert isinstance(degree, int), f"Degree {degree} must be of type Int."

        def round_up_to_even(n):
            if n % 2 == 0:
                return n
            else:
                return n + 1

        max_degree = round_up_to_even(degree)

        if multiplicand is None:
            max_degree_multiplicand = 0

        else:
            state, multiplicand_degrees = polymat.to_degree(
                multiplicand, variables=variables
            ).apply(state)
            max_degree_multiplicand = max(max(multiplicand_degrees))

        max_degree_multiplier = max(max_degree - max_degree_multiplicand, 0)
        degree_range_multiplier = tuple(range(int(max_degree_multiplier) + 1))

        match variables:
            case MatrixExpression():
                variable = variables
            case _:
                variable = polymat.from_variable_indices(variables)

        state, expr = define_polynomial(
            name=name,
            monomials=variable.combinations(degree_range_multiplier).cache(),
        ).apply(state)

        return state, expr

    return statemonad.get_map_put(_define_multiplier)


def define_symmetric_matrix(
    name: str,
    size: int | None = None,
    monomials: MonomialVectorExpression | None = None,
    like: MatrixExpression | None = None,
):
    """
    Defines of a symmetric n x n matrix.

    Args:
        name: The name assigned to the parametrized polynomial. This defines the name of the
            decision variable for each coefficient of the polynomial.
        monomials: Optional monomial vector that determines the structure of the polynomial matrix. If None,
            monomials are assumed to be a single element 1.
        size: The number of rows of the resulting polynomial matrix.

    Returns:
        (StateMonad[MatrixExpression]): A polynomial expression where the coefficients are decision variables.
    """

    if monomials is None:
        monomials = polymat.from_(1).to_monomial_vector()

    def _define_symmetric_matrix(state, monomials=monomials):
        match (size, like):
            case None, MatrixExpression():
                state, (size_, _) = polymat.to_shape(like).apply(state)
            case size_, _:
                pass

        entries = {}

        def gen_rows():
            for row in range(size_):

                def gen_cols():
                    for col in range(size_):
                        if row <= col:
                            param = define_variable(
                                name=f"{name}_{row + 1}_{col + 1}",
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

        return state, init_polynomial_variable(
            name=name,
            monomials=monomials,
            coefficients=params,
            child=expr.child,
            shape=(size_, size_),
        )

    return statemonad.get_map_put(_define_symmetric_matrix)


# def v_stack(expressions: Iterator[MatrixExpression]) -> MatrixExpression:
#     return polymat.v_stack(expressions)
