import mosek
import numpy as np

from dataclassabc import dataclassabc

from sosopt.solvers.solverresult import SolverResult
from sosopt.solvers.solvermixin import SolveInfo, SolverMixin


@dataclassabc(frozen=True)
class MosekSolverResult(SolverResult):
    solution: np.ndarray
    status: str
    iterations: int
    cost: float


class MosekSolver(SolverMixin):
    def solve(self, info: SolveInfo):
        def get_col_indices(n_col):
            n_var = int(np.sqrt(n_col))

            assert np.isclose(n_var, np.sqrt(n_col)), f'{np.sqrt(n_col)=}'
            
            row, col = np.tril_indices(n_var)
            return sorted(np.ravel_multi_index((col, row), (n_var, n_var)))
        
        def gen_s_arrays():
            for array in info.s_data:
                col_indices = get_col_indices(array.n_eq)
                yield array[0][col_indices, :], array[1][col_indices, :]
        
        s_arrays = tuple(gen_s_arrays())

        q = info.lin_cost[1].T
        h = np.vstack(tuple(c[0] for c in s_arrays))
        G = np.vstack(tuple(c[1] for c in s_arrays))

        n_eq = G.shape[0]
        n_var = G.shape[1]

        def get_triplet(G):
            afeidx, varidx = np.nonzero(G)
            f_val = G[afeidx, varidx]
            return tuple(afeidx), tuple(varidx), tuple(f_val)

        afeidx, varidx, f_val = get_triplet(G)

        # if cost.degree == 2:

        if info.quad_cost is not None:
            # nP = int(np.sqrt(cost[2].shape[1]))
            # P = np.sqrt(np.diag(cost[2].reshape(nP, nP).toarray())).reshape(1, -1)
            P = info.quad_cost[1]

            _, varidx_, f_val_ = get_triplet(P)
            varidx = varidx + (n_var,) + varidx_
            f_val = f_val + (1.0,) + f_val_
            n_quad_eq = len(varidx_) + 1
            for row in range(n_quad_eq):
                afeidx += (n_eq + row,)

            # print(len(afeidx), len(varidx), len(f_val))

            n_eq = n_eq + n_quad_eq
            n_var = n_var + 1

            h = np.vstack((h, np.zeros((n_quad_eq, 1))))

            q = np.vstack((q, np.ones((1, 1))))

        with mosek.Task() as task:
            task.appendvars(n_var)
            task.appendafes(n_eq)

            for j in np.nonzero(q)[0]:
                task.putcj(j, q[j, 0])

            inf = 0.0
            for j in range(n_var):
                task.putvarbound(j, mosek.boundkey.fr, -inf, +inf)
    
            task.putafefentrylist(afeidx, varidx, f_val)
            task.putafegslice(0, n_eq, tuple(h))

            index = 0
            for array in s_arrays:
                n_array_eq = array[0].shape[0]
                task.appendacc(task.appendsvecpsdconedomain(n_array_eq), list(range(index, index+n_array_eq)), None)
                index = index + n_array_eq

            if info.quad_cost is not None:
                task.appendacc(task.appendquadraticconedomain(n_quad_eq), list(range(index, index+n_quad_eq)), None)

            task.putobjsense(mosek.objsense.minimize)

            task.optimize()

            solver_result = MosekSolverResult(
                solution=np.array(task.getxx(mosek.soltype.itr)),
                status=task.getsolsta(mosek.soltype.itr),
                iterations=task.getintinf(mosek.iinfitem.intpnt_iter),
                cost=task.getprimalobj(mosek.soltype.itr)
            )

        return solver_result