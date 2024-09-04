from __future__ import annotations

from sosopt.constraints.from_ import (
    sos_constraint as _sos_constraint,
    zero_polynomial_constraint as _zero_polynomial_constraint,
    sos_constraint_matrix as _sos_constraint_matrix,
    sos_constraint_putinar as _sos_constraint_putinar,
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
from sosopt.problem import sos_problem as _sos_problem

cvx_opt_solver = CVXOPTSolver()
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
sos_constraint_matrix = _sos_constraint_matrix
sos_constraint_putinar = _sos_constraint_putinar

# Defining the SOS Optimization Problem
solve_args = _get_solver_args  # depricate
solver_args = _get_solver_args
sos_problem = _sos_problem
