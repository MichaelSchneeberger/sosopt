from __future__ import annotations

from sosopt.constraints.from_ import (
    sos_constraint as _sos_constraint,
    zero_polynomial_constraint as _zero_polynomial_constraint,
    sos_constraint_matrix as _sos_constraint_matrix,
    sos_constraint_putinar as _sos_constraint_putinar,
)
# from sosopt.utils.grammatrix import to_gram_matrix as _to_gram_matrix
from sosopt.polymat.init import (
    init_polynomial_variable as _init_polynomial_variable,
    init_symmetric_matrix_variable as _init_symmetric_matrix_variable,
)
from sosopt.polymat.from_ import define_variable as _define_variable
from sosopt.solvers.cvxoptsolver import CVXOPTSolver
from sosopt.solvers.moseksolver import MosekSolver
from sosopt.solvers.solveargs import get_solver_args as _get_solver_args
from sosopt.constraints.putinarpsatzconstraint import (
    define_multiplier as _define_multiplier,
)
from sosopt.semialgebraicset import set_ as _set_
from sosopt.problem import sos_problem as _sos_problem

cvx_opt_solver = CVXOPTSolver()
mosek_solver = MosekSolver()

# Creating Optimization Variables
define_variable = _define_variable
define_polynomial = _init_polynomial_variable
define_symmetric_matrix = _init_symmetric_matrix_variable
define_multiplier = _define_multiplier

# # Polynomial Expression Manipulations
# to_gram_matrix = _to_gram_matrix

# Constraint Definition
zero_polynomial_constraint = _zero_polynomial_constraint
sos_constraint = _sos_constraint
sos_constraint_matrix = _sos_constraint_matrix
sos_constraint_putinar = _sos_constraint_putinar

set_ = _set_

solve_args = _get_solver_args  # depricate
solver_args = _get_solver_args
sos_problem = _sos_problem
