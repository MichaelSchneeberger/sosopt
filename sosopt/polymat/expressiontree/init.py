from dataclassabc import dataclassabc

from polymat.utils.getstacklines import FrameSummary
from polymat.expressiontree.data.variables import VariableType
from polymat.expressiontree.nodes import (
    ExpressionNode,
)
from polymat.expressiontree.init import init_quadratic_monomials

from sosopt.polymat.expressiontree.quadraticcoefficients import QuadraticCoefficients


@dataclassabc(frozen=True, repr=False)
class QuadraticCoefficientsImpl(QuadraticCoefficients):
    child: ExpressionNode
    monomials: ExpressionNode
    variables: VariableType
    ignore_unmatched: bool
    stack: tuple[FrameSummary, ...]


def init_quadratic_coefficients(
    child: ExpressionNode,
    variables: VariableType,
    stack: tuple[FrameSummary, ...],
    monomials: ExpressionNode | None = None,
    ignore_unmatched: bool = False,
):
    if monomials is None:
        monomials = init_quadratic_monomials(child=child, variables=variables)

    return QuadraticCoefficientsImpl(
        child=child,
        variables=variables,
        monomials=monomials,
        ignore_unmatched=ignore_unmatched,
        stack=stack,
    )
