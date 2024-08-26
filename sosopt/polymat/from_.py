from typing import Iterator
import polymat

from polymat.typing import MatrixExpression

from sosopt.polymat.decisionvariablesymbol import DecisionVariableSymbol


def define_variable(
    name: str,
    size: int | MatrixExpression | None = None,
):
    variable = DecisionVariableSymbol(name)

    return polymat.define_variable(
        name=variable,
        size=size,
    )


def v_stack(expressions: Iterator[MatrixExpression]) -> MatrixExpression:
    return polymat.v_stack(expressions)
