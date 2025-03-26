import abc
from collections import Counter
import itertools
import math
from typing import override

from polymat.expressiontree.nodes import (
    SingleChildExpressionNode,
)
from polymat.sparserepr.data.monomial import sort_monomial, sort_monomials
from polymat.sparserepr.init import init_sparse_repr_from_iterable
from polymat.sparserepr.sparserepr import SparseRepr
from polymat.state.state import State


class QuadraticMonomialVector(SingleChildExpressionNode):
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

        def gen_monomials():
            for _, polynomial in child.entries():
                for monomial in polynomial.keys():
                    yield tuple(
                        (index, power) for index, power in monomial if index in indices
                    )

        monomials = set(gen_monomials())

        def gen_monomial_degrees():
            for monomial in monomials:
                yield sum(d for _, d in monomial)

        monomial_degrees = tuple(gen_monomial_degrees())

        min_deg = min(math.floor(d / 2) for d in monomial_degrees)
        max_deg = max(math.ceil(d / 2) for d in monomial_degrees)

        def gen_min_max_degree_per_index():
            for var_index in indices:

                def gen_degrees_per_variable():
                    for monomial in monomials:
                        for index, power in monomial:
                            if index == var_index:
                                yield power
                    yield 0

                min_deg = min(math.floor(v / 2) for v in gen_degrees_per_variable())
                max_deg = max(math.ceil(v / 2) for v in gen_degrees_per_variable())

                yield var_index, (min_deg, max_deg)

        min_max_degree_per_index = dict(gen_min_max_degree_per_index())

        def gen_combinations():
            for degree in range(min_deg, max_deg + 1):
                yield from itertools.combinations_with_replacement(indices, degree)

        def acc_combinations(acc, index_combination):
            state, filtered_monomials = acc

            def gen_filtered_monomials():
                monomial = sort_monomial(tuple(Counter(index_combination).items()))

                def is_candidate():
                    for var_index, count in monomial:
                        min_deg, max_deg = min_max_degree_per_index[var_index]

                        if not (min_deg <= count <= max_deg):
                            return False

                    return True

                if is_candidate():
                    yield monomial
                    
            return state, filtered_monomials + tuple(gen_filtered_monomials())

        *_, (state, monomials) = itertools.accumulate(
            gen_combinations(),
            acc_combinations,
            initial=(state, tuple()),
        )

        sorted_monomials = sort_monomials(monomials)

        def gen_polynomial_matrix():
            for index, monomial in enumerate(sorted_monomials):
                yield (index, 0), {monomial: 1.0}

        polymatrix = init_sparse_repr_from_iterable(
            data=gen_polynomial_matrix(),
            shape=(len(sorted_monomials), 1),
        )

        return state, polymatrix
