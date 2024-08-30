from dataclasses import replace
from dataclassabc import dataclassabc

from donotation import do

import statemonad

from polymat.typing import PolynomialExpression, VariableVectorExpression, State

from sosopt.constraints.utils.decisionvariablesmixin import to_decision_variable_symbols
from sosopt.constraints.utils.polynomialvariablesmixin import to_polynomial_variables
from sosopt.constraints.positivepolynomialconstraint import PositivePolynomialConstraint
from sosopt.constraints.putinarpsatzconstraint import (
    PutinarsPsatzConstraint,
    define_multipliers,
    get_sos_polynomial,
)
from sosopt.polymat.abc import (
    PolynomialVariable,
)
from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol
from sosopt.semialgebraicset import SemialgebraicSet


@dataclassabc(frozen=True)
class PositivePolynomialConstraintImpl(PositivePolynomialConstraint):
    name: str
    condition: PolynomialExpression
    decision_variable_symbols: tuple[DecisionVariableSymbol, ...]
    polynomial_variables: VariableVectorExpression

    def copy(self, /, **others):
        return replace(self, **others)


def to_positive_polynomial_constraint(
    name: str,
    condition: PolynomialExpression,
):
    """
    Given the polynomial,
    """

    @do()
    def init_positive_polynomial_constraint():
        polynomial_variables = yield from to_polynomial_variables(condition)
        decision_variable_symbols = yield from to_decision_variable_symbols(condition)

        constraint = PositivePolynomialConstraintImpl(
            name=name,
            condition=condition,
            decision_variable_symbols=decision_variable_symbols,
            polynomial_variables=polynomial_variables,
        )
        return statemonad.from_[State](constraint)

    return init_positive_polynomial_constraint()


@dataclassabc(frozen=True)
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


def to_putinar_psatz_constraint(
    name: str,
    condition: PolynomialExpression,
    domain: SemialgebraicSet,
):
    @do()
    def init_putinar_psatz_constraint():
        polynomial_variables = yield from to_polynomial_variables(condition)

        multipliers = yield from define_multipliers(
            name=name,
            condition=condition,
            domain=domain,
            variables=polynomial_variables,
        )
        sos_polynomial = get_sos_polynomial(
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

    return init_putinar_psatz_constraint()
