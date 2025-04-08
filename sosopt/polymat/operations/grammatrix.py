import abc
import itertools
from typing import override

import polymat
from polymat.abc import FrameSummaryMixin, ExpressionNode, SingleChildExpressionNode
from polymat.typing import SparseRepr

from sosopt.polymat.symbols.auxiliaryvariablesymbol import AuxiliaryVariableSymbol
from sosopt.state.state import State


class GramMatrix(FrameSummaryMixin, SingleChildExpressionNode[State]):
    @property
    @abc.abstractmethod
    def monomials(self) -> ExpressionNode[State]: ...

    @property
    @abc.abstractmethod
    def variables(self) -> SingleChildExpressionNode.VariableType: ...

    @property
    @abc.abstractmethod
    def auxilliary_variable_symbol(self) -> AuxiliaryVariableSymbol | None: ...

    def __str__(self):
        return f"sos_smr({self.child}, {self.variables})"

    @override
    def apply(self, state: State) -> tuple[State, SparseRepr]:
        state, child = self.child.apply(state=state)
        state, monomial_vector = self.monomials.apply(state=state)
        state, indices = self.to_variable_indices(state, self.variables)

        monomial_degree = SparseRepr.monomial_op.monomial_degree
        sort_monomial = SparseRepr.monomial_op.sort_monomial
        add_monomials = SparseRepr.monomial_op.add_monomials
        add_polynomial = SparseRepr.polynomial_matrix_op.add_polynomial_to_polynomial_matrix_mutable

        if not (child.shape == (1, 1)):
            raise AssertionError(
                self.to_operator_traceback(
                    message=f"{child.shape=} is not (1, 1)",
                    stack=self.stack,
                )
            )

        # keep order of monomials
        monomials = tuple(monomial_vector.to_monomials())

        # group all combinations of monomial pairs that result in the same monomial when multiplied together
        monomials_prod = {}
        for (row, row_monom), (col, col_monom) in itertools.product(enumerate(monomials), repeat=2):
            if col <= row:
                # if abs(monomial_degree(row_monom) - monomial_degree(col_monom)) <= 1:
                # print(f'{row_monom=}, {col_monom=}')
                monom = sort_monomial(add_monomials(row_monom, col_monom))
                if monom not in monomials_prod:
                    monomials_prod[monom] = []
                monomials_prod[monom].append((row, col))

        if self.auxilliary_variable_symbol in state.indices:
            start, _ = state.indices[self.auxilliary_variable_symbol]
            current_symbol_index = start

        else:
            current_symbol_index = state.n_indices

        data = {}

        for monomial, monomial_indices in monomials_prod.items():
            if 1 < len(monomial_indices):

                start_symbol_index = current_symbol_index

                for index in monomial_indices[1:]:
                    add_polynomial(
                        mutable=data,
                        index=index,
                        polynomial={((current_symbol_index, 1),): 1},
                    )

                    current_symbol_index += 1

                add_polynomial(
                    mutable=data,
                    index=monomial_indices[0],
                    polynomial={((index, 1),): -1 for index in range(start_symbol_index, current_symbol_index)},
                )

        size = current_symbol_index - state.n_indices

        if self.auxilliary_variable_symbol in state.indices:
            start, stop = state.indices[self.auxilliary_variable_symbol]

            assert current_symbol_index == stop, f'{current_symbol_index} does not equal {stop}'

        else:
            state, _ = state.register(
                size=current_symbol_index - state.n_indices,
                symbol=self.auxilliary_variable_symbol,
                stack=self.stack,
            )

        polynomial = child.at(0, 0)

        if polynomial:
            for monomial, value in polynomial.items():
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
                        self.to_operator_traceback(
                            message=f"{x_monomial=} not in {monomials_prod}",
                            stack=self.stack,
                        )
                    )
                
                monomial_indices = monomials_prod[x_monomial]

                add_polynomial(
                    mutable=data,
                    index=monomial_indices[0],
                    polynomial={p_monomial: value},
                )

        size = monomial_vector.shape[0]
        polymatrix = polymat.init_sparse_repr_from_data(
            data=data,
            shape=(size, size),
        )

        return state, polymatrix

        # print(x_monomial)
        
        # monomial_indices = monomials_prod[x_monomial]

        # match monomial_indices:
        #     case (index,):
        #         add_polynomial_to_polynomial_matrix_mutable(
        #             mutable=data,
        #             index=index,
        #             polynomial={p_monomial: value},
        #         )

        #     case _:
        #         # left, right = split_monomial_indices(x_monomial)
        #         # row = monomials.index(left)
        #         # col = monomials.index(right)
        #         # diag_index = row, col

        #         anonymous_indices = []
        #         for index in monomial_indices[1:]:
        #             state, (anonymous_index, _) = state.register(
        #                 size=1,
        #                 stack=self.stack,
        #             )
        #             anonymous_indices.append(anonymous_index)

        #             add_polynomial_to_polynomial_matrix_mutable(
        #                 mutable=data,
        #                 index=index,
        #                 polynomial={((anonymous_index, 1),): 1},
        #             )

        #         add_polynomial_to_polynomial_matrix_mutable(
        #             mutable=data,
        #             index=monomial_indices[0],
        #             polynomial={((index, 1),): -1 for index in anonymous_indices} | {p_monomial: value},
        #         )
