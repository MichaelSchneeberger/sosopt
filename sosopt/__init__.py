from __future__ import annotations

from sosopt.polynomialconstraints.from_ import (
    sos_constraint as _sos_constraint,
    zero_polynomial_constraint as _zero_polynomial_constraint,
    sos_matrix_constraint as _sos_matrix_constraint,
    psatz_putinar_constraint as _psatz_putinar_constraint,
)
from sosopt.polymat.from_ import (
    define_multiplier as _define_multiplier,
    define_polynomial as _define_polynomial,
    define_symmetric_matrix as _define_symmetric_matrix,
    define_variable as _define_variable,
)
from sosopt.solvers.cvxoptsolver import CVXOPTSolver
from sosopt.solvers.moseksolver import MosekSolver
from sosopt.solvers.solveargs import get_solver_args as _get_solver_args
from sosopt.semialgebraicset import set_ as _set_
from sosopt.sosproblem import init_sos_problem as _init_sos_problem
from sosopt.conversions import to_linear_cost as _to_linear_cost

cvxopt_solver = CVXOPTSolver()
cvx_opt_solver = cvxopt_solver      # depricated
mosek_solver = MosekSolver()

# Defining Optimization Variables
define_variable = _define_variable
define_polynomial = _define_polynomial
define_symmetric_matrix = _define_symmetric_matrix
define_multiplier = _define_multiplier

# Defining Sets
set_ = _set_

# Defining Constraint
zero_polynomial_constraint = _zero_polynomial_constraint
sos_constraint = _sos_constraint
sos_matrix_constraint = _sos_matrix_constraint
sos_constraint_matrix = _sos_matrix_constraint      # depricated
psatz_putinar_constraint = _psatz_putinar_constraint
sos_constraint_putinar = _psatz_putinar_constraint      # depricated

# Defining the SOS Optimization Problem
solve_args = _get_solver_args  # depricate
solver_args = _get_solver_args
sos_problem = _init_sos_problem

# conversions
to_linear_cost = _to_linear_cost
