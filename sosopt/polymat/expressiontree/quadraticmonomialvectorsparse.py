import abc
from typing import override

# from polymat.expressiontree.data.variables import VariableType, to_indices
from polymat.expressiontree.nodes import (
    SingleChildExpressionNode,
)
from polymat.sparserepr.data.monomial import sort_monomials, split_monomial_indices
from polymat.sparserepr.init import init_sparse_repr_from_iterable
from polymat.sparserepr.sparserepr import SparseRepr
from polymat.state.state import State


class QuadraticMonomialVectorSparse(SingleChildExpressionNode):
    """
    Constructs the monomial vector Z(x) corresponding to the quadratic form of the polynomial.
    Given a vector of variables, this class generates the set of monomials involved in the
    quadratic form p(x) = Z(x)^\top Q Z(x), where Q is the coefficient matrix and Z(x) is the 
    vector of monomials.

    Example:
        ```python
        x1 = polymat.define_variable('x1')
        x2 = polymat.define_variable('x2')
        x = polymat.v_stack((x1, x2))

        # Example polynomial
        p = 1 + x1*x2 + x1**2

        # Generate the monomial vector associated with the quadratic form of p
        expr = p.quadratic_monomials_in(x)

        # Convert the result to a sympy expression
        state, expr_sympy = polymat.to_sympy(expr.T).apply(state)

        # The output will be expr_sympy=Matrix([[1, x1, x2]])
        print(f'{expr_sympy=}')

        Args:
            x (VariableVectorExpression): The vector of variables used to construct the 
                                        monomials for the quadratic form.

        Returns:
            QuadraticMonomials: An instance representing the vector of monomials involved 
                                in the quadratic form of the polynomial.
        ```
    """

    @property
    @abc.abstractmethod
    def variables(self) -> SingleChildExpressionNode.VariableType: ...

    def __str__(self):
        return f"quadratic_monomials({self.child}, {self.variables})"

    # overwrites the abstract method of `ExpressionBaseMixin`
    @override
    def apply(self, state: State) -> tuple[State, SparseRepr]:
        state, child = self.child.apply(state=state)
        state, indices = self.to_variable_indices(state, self.variables)

        def gen_linear_monomials():
            for _, polynomial in child.entries():
                for monomial in polynomial.keys():
                    x_monomials = tuple(
                        (index, power) for index, power in monomial if index in indices
                    )

                    left_monomials, right_monomials = split_monomial_indices(
                        x_monomials
                    )

                    yield left_monomials
                    yield right_monomials

        # sort monomials for clearer visual representation in the output
        sorted_monomials = sort_monomials(set(gen_linear_monomials()))

        def gen_polynomial_matrix():
            for index, monomial in enumerate(sorted_monomials):
                yield (index, 0), {monomial: 1.0}

        polymatrix = init_sparse_repr_from_iterable(
            data=gen_polynomial_matrix(),
            shape=(len(sorted_monomials), 1),
        )

        return state, polymatrix
