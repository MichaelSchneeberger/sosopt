import mosek
import numpy as np

from dataclassabc import dataclassabc

from sosopt.solvers.solveargs import SolverArgs
from sosopt.solvers.solverdata import SolutionFound, SolutionNotFound
from sosopt.solvers.solvermixin import SolverMixin


@dataclassabc(frozen=True, slots=True)
class MosekSolutionNotFound(SolutionNotFound):
    status: str


@dataclassabc(frozen=True, slots=True)
class MosekSolutionFound(SolutionFound):
    solution: np.ndarray
    status: str
    iterations: int
    cost: float
    is_successful: bool


class MosekSolver(SolverMixin):
    def solve(self, info: SolverArgs):

        if info.quad_cost is not None:
            raise Exception('Mosek can not solve a quadratic cost.')

        def to_quadratic_size(n):
            n_sqrt = np.sqrt(n)

            assert n_sqrt.is_integer(), f'{n_sqrt=}'

            return int(n_sqrt)

        def to_vectorized_tril_indices(n_col):
            """
            The row indices for a 2x2 matrix are [0, 2, 3].
            """
            size = to_quadratic_size(n_col)
            row, col = np.tril_indices(size)
            return sorted(np.ravel_multi_index((col, row), (size, size)))
        
        def gen_s_arrays():
            for array in info.s_data:
                row_indices = to_vectorized_tril_indices(array.n_eq)

                # Mosek requires only the lower-triangle entries of the semi-definite matrix
                yield array[0][row_indices, :], array[1][row_indices, :]
        
        s_arrays = tuple(gen_s_arrays())

        q = info.lin_cost[1].T
        h = np.vstack(tuple(c[0] for c in s_arrays))
        G = np.vstack(tuple(c[1] for c in s_arrays))

        n_eq = G.shape[0]
        n_var = G.shape[1]

        def to_sparse_representation(G):
            afeidx, varidx = np.nonzero(G)
            f_val = G[afeidx, varidx]
            return tuple(afeidx), tuple(varidx), tuple(f_val)

        G_rows, G_vars, G_vals = to_sparse_representation(G)

        if info.eq_data:
            b = np.vstack(tuple(c[0] for c in info.eq_data))
            A = np.vstack(tuple(-c[1] for c in info.eq_data))

            A_rows, A_vars, A_vals = to_sparse_representation(A)

        with mosek.Task() as task:
            task.appendvars(n_var)
            task.appendafes(n_eq)

            # linear cost
            for j in np.nonzero(q)[0]:
                task.putcj(j, q[j, 0])

            # variable bounds are set to infinity
            inf = 0.0
            for j in range(n_var):
                task.putvarbound(j, mosek.boundkey.fr, -inf, +inf)
    
            # add semi-definite entries
            task.putafefentrylist(G_rows, G_vars, G_vals)
            task.putafegslice(0, n_eq, tuple(h))

            index = 0

            # indicate which semi-definite entries belong to which semi-definite constraint
            for array in s_arrays:
                n_array_eq = array[0].shape[0]
                task.appendacc(task.appendsvecpsdconedomain(n_array_eq), list(range(index, index+n_array_eq)), None)
                index = index + n_array_eq

            if info.eq_data:
                n_lin_eq = A.shape[0]

                task.appendcons(n_lin_eq)
                task.putaijlist(A_rows, A_vars, A_vals)
                task.putconboundslice(0, n_lin_eq, tuple(mosek.boundkey.fx for _ in b), tuple(b), tuple(b))

            task.putobjsense(mosek.objsense.minimize)

            task.optimize()

            # Get status information about the solution
            status = task.getsolsta(mosek.soltype.itr)

            if (status == mosek.solsta.optimal):
                solver_result = MosekSolutionFound(
                    solution=np.array(task.getxx(mosek.soltype.itr)),
                    status=status,
                    iterations=task.getintinf(mosek.iinfitem.intpnt_iter),
                    cost=task.getprimalobj(mosek.soltype.itr),
                    is_successful=True,
                )
            else:
                solver_result = MosekSolutionNotFound(
                    status=status,
                )

        return solver_result