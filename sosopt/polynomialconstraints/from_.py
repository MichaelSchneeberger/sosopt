from __future__ import annotations

import statemonad

import polymat
from polymat.typing import (
    MatrixExpression,
    SymmetricMatrixExpression,
)

from sosopt.polynomialconstraints.quadraticmoduleconstraint import init_quadratic_module_constraint
from sosopt.polynomialconstraints.sumofsqauresconstraint import init_sum_of_squares_constraint
from sosopt.polynomialconstraints.zeropolynomialconstraint import init_zero_polynomial_constraint
from sosopt.semialgebraicset import SemialgebraicSet


def zero_polynomial_constraint(
    equal_to_zero: MatrixExpression,
    name: str | None = None,
):
    """
    This polynomial constraint ensures that a polynomial expression is zero 
    as a polynomial: All coefficients of the polynomials must be zero.

    Args:
        name: The name of the constraint. 
        equal_to_zero: The polynomial expression whose coefficients must be zero.

    Returns:
        (StateMonad[ZeroPolynomialConstraint]): A polynomial constraint

    Example:
        ``` python
        state, r_zero_constraint = sosopt.zero_polynomial_constraint(
            name='r_zero',
            equal_to_zero=r,
        ).apply(state)
        ```
    """

    return init_zero_polynomial_constraint(
        name=name,
        zero_matrix=equal_to_zero,
    )


def sos_constraint(
    name: str,
    greater_than_zero: MatrixExpression | None = None,
    smaller_than_zero: MatrixExpression | None = None,
):
    """
    This polynomial constraint ensures that a scalar polynomial expression belongs 
    to the SOS Cone.

    Args:
        name: The name of the constraint. 
        greater_than_zero: The polynomial expression that must be SOS.
        smaller_than_zero: The polynomial expression whose negative must be SOS.
            This argument is ignore if greater_than_zero is not None.

    Returns:
        (StateMonad[SumOfSqauresConstraint]): A polynomial constraint

    Example:
        ``` python
        state, r_sos_constraint = sosopt.sos_constraint(
            name='r_sos',
            greater_than_zero=r,
        ).apply(state)
        ```
    """

    if greater_than_zero is not None:
        positive_matrix = greater_than_zero
    elif smaller_than_zero is not None:
        positive_matrix = -smaller_than_zero
    else:
        raise Exception("SOS constraint requires condition.")

    return init_sum_of_squares_constraint(
        name=name,
        positive_matrix=positive_matrix,
    )


def sos_matrix_constraint(
    name: str,
    greater_than_zero: SymmetricMatrixExpression | None = None,
    smaller_than_zero: SymmetricMatrixExpression | None = None,
):
    """
    This polynomial constraint ensures a polynomial matrix expression belongs 
    to the SOS Matrix Cone.

    Args:
        name: The name of the constraint. 
        greater_than_zero: The polynomial expression Q that must be SOS Matrix.
            This means that v^T Q v is SOS for an additional polynomial variable v.
        smaller_than_zero: The polynomial expression whose negative must be SOS Matrix.
            This argument is ignore if greater_than_zero is not None.

    Returns:
        (StateMonad[SumOfSqauresConstraint]): A polynomial constraint

    Example:
        ``` python
        state, q_sos_constraint = sosopt.sos_matrix_constraint(
            name='q_sos',
            greater_than_zero=q,
        ).apply(state)
        ```
    """

    if greater_than_zero is not None:
        condition = greater_than_zero
    elif smaller_than_zero is not None:
        condition = -smaller_than_zero
    else:
        raise Exception("SOS constraint requires condition.")

    def _sos_matrix_constraint(state):

        state, shape = polymat.to_shape(condition).apply(state)

        x = polymat.define_variable(f"{name}_x", size=shape[0])

        constraint = sos_constraint(
            name=name,
            greater_than_zero=x.T @ condition @ x,
        )
        
        return state, constraint

    return statemonad.get_map_put(_sos_matrix_constraint)


def quadratic_module_constraint(
    name: str,
    domain: SemialgebraicSet | None = None,
    greater_than_zero: MatrixExpression | None = None,
    smaller_than_zero: MatrixExpression | None = None,
):
    """
    This polynomial constraint defines a non-negativity condition on a subset of the 
    states space (called the domain) using a quadratic module construction following Putinar's 
    Positivstellensatz.

    Args:
        name: The name of the constraint.
        domain: Defined by a algebraic set.
        greater_than_zero: The polynomial expression that must be non-negative on the domain.
        smaller_than_zero: The polynomial expression that must be non-positive on the domain.
            This argument is ignore if greater_than_zero is not None.

    Returns:
        (StateMonad[QuadraticModuleConstraint]): A polynomial constraint

    Example:
        ``` python
        state, r_qm_constraint = sosopt.quadratic_module_constraint(
            name='r_qm',
            greater_than_zero=r,
            domain=sosopt.set_(
                smaller_than_zero={'w': w},
            )
        ).apply(state)
        ```
    """
    
    if greater_than_zero is not None:
        positive_matrix = greater_than_zero
    elif smaller_than_zero is not None:
        positive_matrix = -smaller_than_zero
    else:
        raise Exception("SOS constraint requires condition.")

    return init_quadratic_module_constraint(
        name,
        expression=positive_matrix,
        domain=domain,
    )