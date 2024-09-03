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
    less_than_zero: dict[str, VectorExpression] = {},
):
    inequalities = greater_than_zero | {n: -p for n, p in less_than_zero.items()}

    return SemialgebraicSet(
        inequalities=inequalities,
        equalities=equal_zero,
    )
