from dataclasses import replace
from dataclassabc import dataclassabc

from donotation import do

import statemonad

import polymat
from polymat.typing import (
    PolynomialExpression,
    VariableVectorExpression,
    State,
    MatrixExpression,
)

from sosopt.constraints.constraintprimitives.constraintprimitive import ConstraintPrimitive
from sosopt.constraints.utils.decisionvariablesmixin import to_decision_variable_symbols
from sosopt.constraints.utils.polynomialvariablesmixin import to_polynomial_variables
from sosopt.constraints.sumofsqauresconstraint import SumOfSqauresConstraint
from sosopt.constraints.putinarpsatzconstraint import (
    PutinarsPsatzConstraint,
    define_psatz_multipliers,
    define_putinars_psatz_condition,
)
from sosopt.constraints.zeropolynomialconstraint import ZeroPolynomialConstraint
from sosopt.polymat.polynomialvariable import (
    PolynomialVariable,
)
from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol
from sosopt.semialgebraicset import SemialgebraicSet


@dataclassabc(frozen=True, slots=True)
class PutinarPsatzConstraintImpl(PutinarsPsatzConstraint):
    condition: PolynomialExpression
    decision_variable_symbols: tuple[DecisionVariableSymbol, ...]
    domain: SemialgebraicSet
    multipliers: dict[str, PolynomialVariable]
    name: str
    polynomial_variables: VariableVectorExpression
    sos_polynomial: PolynomialExpression

    def copy(self, /, **others):
        return replace(self, **others)


@do()
def to_putinar_psatz_constraint(
    name: str,
    condition: PolynomialExpression,
    domain: SemialgebraicSet,
):
    polynomial_variables = yield from to_polynomial_variables(condition)

    multipliers = yield from define_psatz_multipliers(
        name=name,
        condition=condition,
        domain=domain,
        variables=polynomial_variables,
    )
    sos_polynomial = define_putinars_psatz_condition(
        condition=condition,
        domain=domain,
        multipliers=multipliers,
    )
    decision_variable_symbols = yield from to_decision_variable_symbols(
        sos_polynomial
    )

    constraint = PutinarPsatzConstraintImpl(
        name=name,
        condition=condition,
        decision_variable_symbols=decision_variable_symbols,
        polynomial_variables=polynomial_variables,
        domain=domain,
        multipliers=multipliers,
        sos_polynomial=sos_polynomial,
    )
    return statemonad.from_[State](constraint)


@dataclassabc(frozen=True, slots=True)
class SumOfSqauresConstraintImpl(SumOfSqauresConstraint):
    name: str
    condition: PolynomialExpression
    decision_variable_symbols: tuple[DecisionVariableSymbol, ...]
    polynomial_variables: VariableVectorExpression

    def copy(self, /, **others):
        return replace(self, **others)


@do()
def to_sum_of_squares_constraint(
    name: str,
    condition: PolynomialExpression,
):
    """
    Given the polynomial,
    """

    polynomial_variables = yield from to_polynomial_variables(condition)
    decision_variable_symbols = yield from to_decision_variable_symbols(condition)

    constraint = SumOfSqauresConstraintImpl(
        name=name,
        condition=condition,
        decision_variable_symbols=decision_variable_symbols,
        polynomial_variables=polynomial_variables,
    )
    return statemonad.from_[State](constraint)


@dataclassabc(frozen=True, slots=True)
class ZeroPolynomialConstraintImpl(ZeroPolynomialConstraint):
    name: str
    condition: MatrixExpression
    shape: tuple[int, int]
    decision_variable_symbols: tuple[DecisionVariableSymbol, ...]
    polynomial_variables: VariableVectorExpression
    children: tuple[ConstraintPrimitive, ...]

    def copy(self, /, **others):
        return replace(self, **others)


@do()
def init_zero_polynomial_constraint(
    name: str,
    condition: MatrixExpression,
):
    shape = yield from polymat.to_shape(condition)
    polynomial_variables = yield from to_polynomial_variables(condition)
    decision_variable_symbols = yield from to_decision_variable_symbols(condition)

    constraint = ZeroPolynomialConstraintImpl(
        name=name,
        condition=condition,
        shape=shape,
        decision_variable_symbols=decision_variable_symbols,
        polynomial_variables=polynomial_variables,
        children=tuple(),
    )

    return statemonad.from_[State](constraint)
