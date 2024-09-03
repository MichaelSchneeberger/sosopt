from typing import Iterator

import polymat
from polymat.typing import MatrixExpression

from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol


def define_variable(
    name: DecisionVariableSymbol | str,
    size: int | MatrixExpression | None = None,
):
    
    if not isinstance(name, DecisionVariableSymbol):
        symbol = DecisionVariableSymbol(name)
    else:
        symbol = name

    return polymat.define_variable(name=symbol, size=size)

    # if isinstance(size, MatrixExpression):
    #     n_size = size.child
    # else:
    #     n_size = size

    # child=init_define_variable(
    #     symbol=symbol, size=n_size, stack=get_frame_summary()
    # )

    # return init_decision_variable_expression(
    #     child=child,
    #     symbol=symbol,
    # )


def v_stack(expressions: Iterator[MatrixExpression]) -> MatrixExpression:
    return polymat.v_stack(expressions)
