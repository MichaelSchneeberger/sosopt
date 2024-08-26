# collection of polynomials group into inequalities and equalities

from __future__ import annotations
from dataclasses import dataclass

from polymat.typing import VectorExpression


class PolynomialConstraint:
    pass


@dataclass(frozen=True)
class SemialgebraicSet:
    inequalities: dict[str, VectorExpression]
    equalities: dict[str, VectorExpression]
