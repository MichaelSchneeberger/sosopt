from dataclasses import replace
from dataclassabc import dataclassabc

from polymat.typing import MatrixExpression, VariableVectorExpression, VectorExpression

from sosopt.constraints.constraintprimitives.constraintprimitive import (
    ConstraintPrimitive,
)
from sosopt.constraints.constraintprimitives.zeropolynomialprimitive import ZeroPolynomialPrimitive
from sosopt.constraints.constraintprimitives.positivepolynomialprimitive import (
    PositivePolynomialPrimitive,
)
from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol


# @dataclassabc(frozen=True)
# class ZeroPolynomialPrimitiveImpl(ZeroPolynomialPrimitive):
#     name: str
#     condition: VectorExpression
#     n_rows: int
#     decision_variable_symbols: tuple[DecisionVariableSymbol, ...]
#     polynomial_variables: VariableVectorExpression
#     children: tuple[ConstraintPrimitive, ...]
#     volatile_symbols: tuple[DecisionVariableSymbol, ...]

#     def copy(self, /, **others):
#         return replace(self, **others)


# def init_zero_polynomial_primitive(
#     name: str,
#     condition: VectorExpression,
#     decision_variable_symbols: tuple[DecisionVariableSymbol, ...],
#     polynomial_variables: VariableVectorExpression,
#     n_rows: int,
# ):
#     return ZeroPolynomialPrimitiveImpl(
#         name=name,
#         condition=condition,
#         n_rows=n_rows,
#         decision_variable_symbols=decision_variable_symbols,
#         polynomial_variables=polynomial_variables,
#         children=tuple(),
#         volatile_symbols=tuple(),
#     )


@dataclassabc(frozen=True)
class PositivePolynomialPrimitiveImpl(PositivePolynomialPrimitive):
    name: str
    condition: MatrixExpression
    children: tuple[ConstraintPrimitive, ...]
    decision_variable_symbols: tuple[DecisionVariableSymbol, ...]
    volatile_symbols: tuple[DecisionVariableSymbol, ...]
    polynomial_variables: VariableVectorExpression

    def copy(self, /, **others):
        return replace(self, **others)


init_positive_polynomial_primitive = (
    PositivePolynomialPrimitiveImpl
)
