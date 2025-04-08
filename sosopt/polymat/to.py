from sosopt.polymat.sources.polynomialvariable import PolynomialVariable
from sosopt.polymat.symbols.decisionvariablesymbol import DecisionVariableSymbol
import statemonad

import polymat
from polymat.typing import (
    MatrixExpression,
)

from sosopt.state.state import State as BaseState


def to_symbol_values[State: BaseState](variable: PolynomialVariable[State], value: MatrixExpression[State]):
    def _to_symbol_values(state: State):
        symbol_values: dict[DecisionVariableSymbol, tuple[float, ...]] = {}

        for (row, col), param in variable.iterate_coefficients():
            state, (data, *_) = polymat.to_tuple(
                value[row, col].coefficients_vector(monomials=variable.monomials)
            ).apply(state)

            symbol_values[param.symbol] = data
        
        return state, symbol_values

    return statemonad.get_map_put(_to_symbol_values)
