from dataclasses import dataclass
import math
import cvxopt
import numpy as np

from dataclassabc import dataclassabc

from polymat.typing import ArrayRepr

from sosopt.solvers.solveargs import SolverArgs
from sosopt.solvers.solverdata import SolutionFound, SolutionNotFound
from sosopt.solvers.solvermixin import SolverMixin


@dataclass(frozen=True)
class CVXOptSolverData:
    x: np.ndarray
    y: np.ndarray
    s: np.ndarray
    z: np.ndarray
    status: str
    gap: float
    relative_gap: float
    primal_objective: float
    dual_objective: float
    primal_infeasibility: float
    dual_infeasibility: float
    primal_slack: float
    dual_slack: float
    iterations: int


@dataclassabc(frozen=True, slots=True)
class CVXOptSolutionNotFound(CVXOptSolverData, SolutionNotFound):
    pass


@dataclassabc(frozen=True, slots=True)
class CVXOptSolutionFound(CVXOptSolverData, SolutionFound):
    @property
    def solution(self) -> np.ndarray:
        return self.x

    @property
    def cost(self) -> float:
        return self.primal_objective


class CVXOPTSolver(SolverMixin):
    def solve(self, info: SolverArgs):
        def get_dim_s(array: ArrayRepr) -> int:
            dim = np.sqrt(array.n_eq)
            assert math.isclose(int(dim), dim), f"{dim=}"
            return int(dim)

        dim_l = sum(d.n_eq for d in info.l_data)
        dim_q = list(d.n_eq for d in info.q_data)
        dim_s = list(get_dim_s(d) for d in info.s_data)

        inequality_constraints = info.l_data + info.q_data + info.s_data

        q = cvxopt.matrix(info.lin_cost[1].T)

        if inequality_constraints:
            h = cvxopt.matrix(np.vstack(tuple(c[0] for c in inequality_constraints)))
            G = cvxopt.matrix(np.vstack(tuple(-c[1] for c in inequality_constraints)))
        else:
            h = None
            G = None

        if info.eq_data:
            b = cvxopt.matrix(np.vstack(tuple(c[0] for c in info.eq_data)))
            A = cvxopt.matrix(np.vstack(tuple(-c[1] for c in info.eq_data)))
        else:
            b = None
            A = None

        if info.quad_cost is None:
            return_val = cvxopt.solvers.conelp(
                c=q, G=G, h=h, A=A, b=b,
                dims={"l": dim_l, "q": dim_q, "s": dim_s},
            )

        else:
            P = cvxopt.matrix(info.quad_cost[1].T @ info.quad_cost[1])

            return_val = cvxopt.solvers.coneqp(
                P=P, q=q, G=G, h=h, A=A, b=b,
                dims={"l": dim_l, "q": dim_q, "s": dim_s},
            )

        status = return_val["status"]

        if status == "optimal" or status == "unknown":
            solver_data_cls = CVXOptSolutionFound
        else:
            solver_data_cls = CVXOptSolutionNotFound

        solver_result = solver_data_cls(
            x=np.array(return_val["x"]).reshape(-1),
            y=np.array(return_val["y"]).reshape(-1),
            s=np.array(return_val["s"]).reshape(-1),
            z=np.array(return_val["z"]).reshape(-1),
            status=return_val["status"],
            gap=return_val["gap"],
            relative_gap=return_val["relative gap"],
            primal_objective=return_val["primal objective"],
            dual_objective=return_val["dual objective"],
            primal_infeasibility=return_val["primal infeasibility"],
            dual_infeasibility=return_val["dual infeasibility"],
            primal_slack=return_val["primal slack"],
            dual_slack=return_val["dual slack"],
            iterations=return_val["iterations"],
        )

        return solver_result
