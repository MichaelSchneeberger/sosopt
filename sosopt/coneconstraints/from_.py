from polymat.typing import (
    SymmetricMatrixExpression,
    VectorExpression,
)

from sosopt.coneconstraints.equalityconstraint import init_equality_constraint
from sosopt.coneconstraints.semidefiniteconstraint import init_semi_definite_constraint


def semi_definite_constraint(
    name: str,
    greater_than_zero: SymmetricMatrixExpression,
):
    """
    This constraint ensures that a symmetric matrix belongs to the positive semidefinite Cone.

    Args:
        name: The name of the constraint. 
        greater_than_zero: The symmetric matrix that must be positive semi-definite.

    Returns:
        (StateMonad[SemiDefiniteConstraint]): A polynomial constraint

    Example:
        ``` python
        state, q_psd_constraint = sosopt.semidefinite_constraint(
            name='q_psd',
            greater_than_zero=q,
        ).apply(state)
        ```
    """

    return init_semi_definite_constraint(
        name=name,
        expression=greater_than_zero,
    )


def equality_constraint(
    name: str,
    equal_to_zero: VectorExpression,
):
    """
    This constraint ensures that all entries of the polynomial expression are zero.

    Args:
        name: The name of the constraint. 
        equal_to_zero: The polynomial expression that must be zero.

    Returns:
        (StateMonad[EqualityConstraint]): A polynomial constraint

    Example:
        ``` python
        state, eq_constraint = sosopt.equality_constraint(
            name='eq',
            greater_than_zero=eq,
        ).apply(state)
        ```
    """

    return init_equality_constraint(
        name=name,
        expression=equal_to_zero,
    )
