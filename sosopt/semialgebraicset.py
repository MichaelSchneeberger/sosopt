from __future__ import annotations
from dataclasses import dataclass

from polymat.typing import VectorExpression


@dataclass(frozen=True)
class SemialgebraicSet:
    inequalities: dict[str, VectorExpression]
    equalities: dict[str, VectorExpression]


def set_(
    equal_zero: dict[str, VectorExpression] = {},
    greater_than_zero: dict[str, VectorExpression] = {},
    smaller_than_zero: dict[str, VectorExpression] = {},
):
    """
    Define a semialgebraic set from a collection scalar polynomial expressions.

    Args:
        equal_zero: A dictionary of polynomial expressions which evaluate to zero 
            on the set.
        greater_than_zero: A dictionary of polynomial expressions which evaluate
            to a positive number on the set.
        smaller_than_zero: A dictionary of polynomial expressions which evaluate
            to a negative number on the set.

    Returns:
        (SemialgebraicSet): A semi-algebraic set

    Example:
        ``` python
        sosopt.set_(
            smaller_than_zero={'w': w},
            equal_zero={'V': V},
        )
        ```
    """

    inequalities = greater_than_zero | {n: -p for n, p in smaller_than_zero.items()}

    return SemialgebraicSet(
        inequalities=inequalities,
        equalities=equal_zero,
    )
