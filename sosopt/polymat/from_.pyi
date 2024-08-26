from typing import Iterator, overload

from polymat.typing import MatrixExpression, VariableVectorExpression

from sosopt.polymat.decisionvariableexpression import (
    DecisionVariableExpression,
    SingleDimDecisionVariableExpression,
)

@overload
def define_variable(
    name: str,
) -> SingleDimDecisionVariableExpression: ...
@overload
def define_variable(
    name: str,
    size: int | MatrixExpression | None = None,
) -> DecisionVariableExpression: ...
def v_stack(
    expressions: Iterator[DecisionVariableExpression],
) -> VariableVectorExpression: ...
