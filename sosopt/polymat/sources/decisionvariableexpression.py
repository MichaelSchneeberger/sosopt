from polymat.abc import (
    VariableExpression,
)


class DecisionVariableVectorSymbolExpression[_](VariableExpression):
    """
    Expression that is a polynomial variable, i.e. an expression that cannot be
    reduced further.
    """

    # def iterate_symbols(self):
    #     yield self.symbol


class DecisionVariableExpression[_](DecisionVariableVectorSymbolExpression):
    pass
