import abc
import itertools
from typing import override

from polymat.utils.getstacklines import FrameSummaryMixin, to_operator_traceback
from polymat.sparserepr.data.monomial import add_monomials
from polymat.sparserepr.data.polynomialmatrix import add_polynomial_to_polynomial_matrix_mutable
from polymat.sparserepr.sparserepr import SparseRepr
from polymat.sparserepr.init import init_sparse_repr_from_data
from polymat.expressiontree.nodes import (
    ExpressionNode,
    SingleChildExpressionNode,
)

from sosopt.state.state import State as BaseState


class GramMatrixUsingEqConstr[State: BaseState](
    FrameSummaryMixin, 
    SingleChildExpressionNode[State],
):
    @property
    @abc.abstractmethod
    def monomials(self) -> ExpressionNode[State]: ...

    @property
    @abc.abstractmethod
    def variables(self) -> SingleChildExpressionNode.VariableType: ...

    # @property
    # @abc.abstractmethod
    # def ignore_unmatched(self) -> bool: ...

    def __str__(self):
        return f"quadratic_in({self.child}, {self.variables})"

    @override
    def apply(self, state: State) -> tuple[State, SparseRepr]:
        state, child = self.child.apply(state=state)
        state, monomial_vector = self.monomials.apply(state=state)
        state, indices = self.to_variable_indices(state, self.variables)

        if not (child.shape == (1, 1)):
            raise AssertionError(
                to_operator_traceback(
                    message=f"{child.shape=} is not (1, 1)",
                    stack=self.stack,
                )
            )

        # keep order of monomials
        monomials = tuple(monomial_vector.to_monomials())
        print(monomials)

        # group all combinations of monomial pairs that result in the same monomial when multiplied together
        monomials_prod = {}
        for (col, col_monom), (row, row_monom) in itertools.product(enumerate(monomials), repeat=2):
            if col <= row:
                monom = add_monomials(col_monom, row_monom)
                print(f'{col_monom=}, {row_monom=}, {monom=}')
                if monom not in monomials_prod:
                    monomials_prod[monom] = []
                monomials_prod[monom].append((col, row))
        print(monomials_prod)

        auxilliary_equations = []
        data = {}

        # def gen_polymatrix():
        polynomial = child.at(0, 0)

        if polynomial:
            for monomial, value in polynomial.items():  # type: ignore
                x_monomial = tuple(
                    (index, count) 
                    for index, count in monomial 
                    if index in indices
                )
                p_monomial = tuple(
                    (index, count)
                    for index, count in monomial
                    if index not in indices
                )

                if x_monomial not in monomials_prod:
                    raise AssertionError(
                        to_operator_traceback(
                            message=f"{x_monomial=} not in {monomials_prod}",
                            stack=self.stack,
                        )
                    )
                
                monomial_indices = monomials_prod[x_monomial]
                # n_indices = len(monomial_indices)

                match monomial_indices:
                    case (index,):
                        # if index not in data:
                        #     data[index] = {}

                        # data[index] |= {p_monomial: value}
                        add_polynomial_to_polynomial_matrix_mutable(
                            mutable=data,
                            index=index,
                            polynomial={p_monomial: value},
                        )

                    case _:
                        # if 1 < n_indices, introduce a variable for each entry and create an equality constraint
                        # c1 + c2 + c3 = p

                        var_indices = []
                        for col, row in monomial_indices:
                            # symbol = DecisionVariableSymbol(self.name)
                            state, (var_index, _) = state.register(
                                size=1,
                                stack=self.stack,
                            )
                            var_indices.append(var_index)

                            # yield (col, row), {variable: value}
                            add_polynomial_to_polynomial_matrix_mutable(
                                mutable=data,
                                index=index,
                                polynomial={((var_index, 1),): value},
                            )

                        auxilliary_equations.append(
                            {((var_index, 1),): -1 for var_index in var_indices} | {p_monomial: value}
                        )

        # print(auxilliary_equations)
        state = state.copy(
            auxilliary_equations=tuple(auxilliary_equations),
        )

        size = monomial_vector.shape[0]
        polymatrix = init_sparse_repr_from_data(
            data=data,
            shape=(size, size),
        )

        return state, polymatrix
