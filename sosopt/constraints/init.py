from dataclasses import replace
from dataclassabc import dataclassabc

from donotation import do

import statemonad

from polymat.typing import PolynomialExpression, VariableVectorExpression, State

from sosopt.constraints.decisionvariablesmixin import to_decision_variable_symbols
from sosopt.constraints.polynomialvariablesmixin import to_polynomial_variables
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
):  # -> StateMonad[State, PositivePolynomialConstraintImpl]:
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
):  # -> StateMonad[State, PutinarPsatzConstraintImpl]:
    @do()
    def init_putinar_psatz_constraint():
        # print('to polynomial variable')
        polynomial_variables = yield from to_polynomial_variables(condition)

        # value = yield from polymat.to_sympy(polynomial_variables)
        # print(f'{value=}')

        # print('get multipliers')
        multipliers = yield from define_multipliers(
            name=name,
            condition=condition,
            domain=domain,
            variables=polynomial_variables,
        )
        # print('define sos polynomial')
        sos_polynomial = get_sos_polynomial(
            condition=condition,
            domain=domain,
            multipliers=multipliers,
        )
        # print('get decision variables')
        decision_variable_symbols = yield from to_decision_variable_symbols(sos_polynomial)

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
