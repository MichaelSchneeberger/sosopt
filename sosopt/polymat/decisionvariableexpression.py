from polymat.typing import (
    VariableExpression,
)


class DecisionVariableExpression(VariableExpression):
    """
    Expression that is a polynomial variable, i.e. an expression that cannot be
    reduced further.
    """

    def iterate_symbols(self):
        yield self.symbol


class SingleValueDecisionVariableExpression(DecisionVariableExpression):
    pass
