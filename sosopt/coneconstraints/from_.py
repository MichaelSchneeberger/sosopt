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
    return init_semi_definite_constraint(
        name=name,
        expression=greater_than_zero,
    )

def equality_constraint(
    name: str,
    equal_to_zero: VectorExpression,
):
    return init_equality_constraint(
        name=name,
        expression=equal_to_zero,
    )
