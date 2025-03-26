from typing import override
from dataclasses import replace
from dataclassabc import dataclassabc

from polymat.utils.getstacklines import FrameSummary
from polymat.typing import (
    ExpressionNode,
    VariableExpression,
    MonomialVectorExpression,
)

from sosopt.polymat.decisionvariableexpression import (
    DecisionVariableVectorSymbolExpression,
)
from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol
from sosopt.polymat.polynomialvariable import (
    PolynomialMatrixVariable,
    ScalarPolynomialVariable,
)
from sosopt.polymat.expressiontree.quadraticmonomialvector import (
    QuadraticMonomialVector,
)
from sosopt.polymat.expressiontree.quadraticmonomialvectorsparse import (
    QuadraticMonomialVectorSparse,
)
from sosopt.polymat.expressiontree.squarematricialrepresentation import (
    SquareMatricialRepresentation,
)
from sosopt.polymat.expressiontree.squarematricialrepresentationsparse import (
    SquareMatricialRepresentationSparse,
)


@dataclassabc(frozen=True, slots=True)
class DecisionVariableExpressionImpl(DecisionVariableVectorSymbolExpression):
    child: ExpressionNode
    symbol: DecisionVariableSymbol

    @override
    def copy(self, /, **changes):
        return replace(self, **changes)


def init_decision_variable_expression(
    child: ExpressionNode, symbol: DecisionVariableSymbol
):
    return DecisionVariableExpressionImpl(
        child=child,
        symbol=symbol,
    )


@dataclassabc(frozen=True, slots=True)
class PolynomialMatrixVariableImpl(PolynomialMatrixVariable):
    name: str
    child: ExpressionNode
    coefficients: tuple[tuple[VariableExpression]]
    shape: tuple[int, int]
    monomials: MonomialVectorExpression

    @override
    def copy(self, /, **changes):
        return replace(self, **changes)


@dataclassabc(frozen=True, slots=True)
class ScalarPolynomialVariableImpl(ScalarPolynomialVariable):
    name: str
    child: ExpressionNode
    coefficient: VariableExpression
    monomials: MonomialVectorExpression

    @override
    def copy(self, /, **changes):
        return replace(self, **changes)


def init_polynomial_variable(
    name: str,
    child: ExpressionNode,
    coefficients: tuple[tuple[VariableExpression]],
    monomials: MonomialVectorExpression,
    shape: tuple[int, int] = (1, 1),
):
    if shape == (1, 1):
        return ScalarPolynomialVariableImpl(
            name=name,
            monomials=monomials,
            coefficient=coefficients[0][0],
            child=child,
        )
    else:
        return PolynomialMatrixVariableImpl(
            name=name,
            monomials=monomials,
            coefficients=coefficients,
            child=child,
            shape=shape,
        )


@dataclassabc(frozen=True, repr=False)
class SquareMatricialRepresentationImpl(SquareMatricialRepresentation):
    child: ExpressionNode
    monomials: ExpressionNode
    variables: SquareMatricialRepresentation.VariableType
    ignore_unmatched: bool
    stack: tuple[FrameSummary, ...]


def init_square_matricial_representation(
    child: ExpressionNode,
    variables: SquareMatricialRepresentation.VariableType,
    stack: tuple[FrameSummary, ...],
    monomials: ExpressionNode | None = None,
    ignore_unmatched: bool = False,
):
    if monomials is None:
        monomials = init_quadratic_monomial_vector(child=child, variables=variables)

    return SquareMatricialRepresentationImpl(
        child=child,
        variables=variables,
        monomials=monomials,
        ignore_unmatched=ignore_unmatched,
        stack=stack,
    )


@dataclassabc(frozen=True, repr=False)
class SquareMatricialRepresentationSparseImpl(SquareMatricialRepresentationSparse):
    child: ExpressionNode
    monomials: ExpressionNode
    variables: ExpressionNode.VariableType
    ignore_unmatched: bool
    stack: tuple[FrameSummary, ...]


def init_square_matricial_representation_sparse(
    child: ExpressionNode,
    variables: ExpressionNode.VariableType,
    stack: tuple[FrameSummary, ...],
    monomials: ExpressionNode | None = None,
    ignore_unmatched: bool = False,
):
    if monomials is None:
        monomials = init_quadratic_monomial_vector_sparse(
            child=child, variables=variables
        )

    return SquareMatricialRepresentationSparseImpl(
        child=child,
        variables=variables,
        monomials=monomials,
        ignore_unmatched=ignore_unmatched,
        stack=stack,
    )


@dataclassabc(frozen=True, repr=False)
class QuadraticMonomialVectorImpl(QuadraticMonomialVector):
    child: ExpressionNode
    variables: QuadraticMonomialVector.VariableType


def init_quadratic_monomial_vector(
    child: ExpressionNode,
    variables: QuadraticMonomialVector.VariableType,
):
    return QuadraticMonomialVectorImpl(
        child=child,
        variables=variables,
    )


@dataclassabc(frozen=True, slots=True)
class QuadraticMonomialVectorSparseImpl(QuadraticMonomialVectorSparse):
    child: ExpressionNode
    variables: ExpressionNode.VariableType


def init_quadratic_monomial_vector_sparse(
    child: ExpressionNode,
    variables: ExpressionNode.VariableType,
):
    return QuadraticMonomialVectorSparseImpl(child=child, variables=variables)
