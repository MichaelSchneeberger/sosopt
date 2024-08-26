from polymat.typing import (
    VectorExpression,
    RowVectorExpression,
    PolynomialExpression,
)
from sosopt.polymat.polynomialvariable import (
    PolynomialVariable as _PolynomialVariable,
)

PolynomialMatrixVariable = _PolynomialVariable

class PolynomialVectorVariable(PolynomialMatrixVariable, VectorExpression): ...
class PolynomialRowVectorVariable(PolynomialMatrixVariable, RowVectorExpression): ...
class PolynomialVariable(
    PolynomialVectorVariable, PolynomialExpression
): ...
