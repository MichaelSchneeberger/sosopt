# from polymat.typing import (
#     VectorExpression,
#     RowVectorExpression,
#     PolynomialExpression,
# )

from sosopt.polymat.decisionvariableexpression import (
    DecisionVariableExpression as _DecisionVariableExpression,
    SingleDimDecisionVariableExpression as _SingleDimDecisionVariableExpression,
)
from sosopt.polymat.polynomialvariable import (
    PolynomialVariable as _PolynomialVariable,
)


DecisionVariableExpression = _DecisionVariableExpression
SingleDimDecisionVariableExpression = _SingleDimDecisionVariableExpression
PolynomialMatrixVariable = _PolynomialVariable
PolynomialVectorVariable = _PolynomialVariable
PolynomialRowVectorVariable = _PolynomialVariable
PolynomialVariable = _PolynomialVariable
